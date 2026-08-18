#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

from CTFd.models import UserTokens
from CTFd.utils import get_config
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user

GITHUB_REQUESTS = "CTFd.utils.git.github.requests.request"
GITLAB_REQUESTS = "CTFd.utils.git.gitlab.requests.request"


def fake_api(responses):
    calls = []

    def side_effect(method, url, **kwargs):
        calls.append((method, url, kwargs))
        for (m, fragment), resp in responses:
            if m == method and fragment in url:
                mock = Mock()
                mock.status_code = resp.get("status", 200)
                mock.json.return_value = resp.get("json")
                mock.headers = {"content-type": "application/json"}
                return mock
        raise AssertionError(f"Unexpected request: {method} {url}")

    side_effect.calls = calls
    return side_effect


def setup_client(app):
    # The test client injects the CSRF token automatically for json requests
    client = app.test_client()
    client.get("/setup")  # Populate session with nonce
    return client


def test_git_admin_only_after_setup():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = login_as_user(app)
        assert user.get("/setup/git").status_code == 403
        assert (
            user.post(
                "/setup/git/github/token",
                json={"token": "x"},
            ).status_code
            == 403
        )

        # Admins manage the integration after setup
        admin = login_as_user(app, "admin")
        r = admin.get("/setup/git")
        assert r.status_code == 200
        assert r.get_json()["data"]["configured"] == {
            "provider": None,
            "repository": None,
        }
    destroy_ctfd(app)


def test_git_admin_manage():
    app = create_ctfd()
    with app.app_context():
        from nacl import encoding, public

        public_key = (
            public.PrivateKey.generate()
            .public_key.encode(encoding.Base64Encoder())
            .decode()
        )
        admin = login_as_user(app, "admin")
        api = fake_api(
            [
                (("GET", "/user"), {"json": {"login": "octocat"}}),
                (("GET", "/contents/.ctf/config"), {"json": {}}),
                (
                    ("GET", "/contents/.github/workflows/sync.yml"),
                    {"status": 404, "json": {}},
                ),
                (
                    ("PUT", "/contents/.github/workflows/sync.yml"),
                    {"status": 201, "json": {}},
                ),
                (
                    ("GET", "/actions/secrets/public-key"),
                    {"json": {"key_id": "1234", "key": public_key}},
                ),
                (("PUT", "/actions/secrets/"), {"status": 201, "json": {}}),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            r = admin.post(
                "/setup/git/github/token",
                json={"token": "gh_token"},
            )
            assert r.status_code == 200

            # Linking as admin provisions credentials and CI immediately
            r = admin.post(
                "/setup/git/github/repositories",
                json={
                    "action": "select",
                    "repository": {
                        "id": "octocat/challenges",
                        "name": "octocat/challenges",
                        "default_branch": "main",
                    },
                },
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["provisioned"] is True

        assert get_config("git_provider") == "github"
        assert get_config("git_repository") == "octocat/challenges"
        first_token = UserTokens.query.one()
        assert get_config("git_token_id") == first_token.id
        secret_puts = [
            url
            for method, url, _ in api.calls
            if method == "PUT" and "/actions/secrets/CTFCLI" in url
        ]
        assert len(secret_puts) == 2
        assert any(
            method == "PUT" and "sync.yml" in url for method, url, _ in api.calls
        )

        # Re-linking rotates the sync token
        with patch(GITHUB_REQUESTS, side_effect=api):
            r = admin.post(
                "/setup/git/github/repositories",
                json={
                    "action": "select",
                    "repository": {
                        "id": "octocat/challenges",
                        "name": "octocat/challenges",
                        "default_branch": "main",
                    },
                },
            )
            assert r.status_code == 200
        second_token = UserTokens.query.one()
        assert second_token.id != first_token.id

        # Disconnecting clears the configuration and revokes the token
        r = admin.delete("/setup/git", json={})
        assert r.status_code == 200
        assert get_config("git_provider") is None
        assert get_config("git_repository") is None
        assert get_config("git_token_id") is None
        assert UserTokens.query.count() == 0
    destroy_ctfd(app)


def test_git_unknown_provider():
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)
        r = client.post(
            "/setup/git/bitbucket/token",
            json={"token": "x"},
        )
        assert r.status_code == 404
    destroy_ctfd(app)


def test_git_github_token_and_select():
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)

        repos = [
            {
                "full_name": "octocat/challenges",
                "default_branch": "main",
                "private": True,
                "html_url": "https://github.com/octocat/challenges",
                "permissions": {"push": True},
            },
            {
                "full_name": "octocat/readonly",
                "default_branch": "main",
                "private": False,
                "html_url": "https://github.com/octocat/readonly",
                "permissions": {"push": False},
            },
        ]
        api = fake_api(
            [
                (("GET", "/user/repos"), {"json": repos}),
                (("GET", "/user"), {"json": {"login": "octocat"}}),
                (("GET", "/contents/.ctf/config"), {"json": {}}),
                (
                    ("GET", "/contents/.github/workflows/sync.yml"),
                    {"status": 404, "json": {}},
                ),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            # Invalid token is rejected
            bad_api = fake_api([(("GET", "/user"), {"status": 401, "json": {}})])
            with patch(GITHUB_REQUESTS, side_effect=bad_api):
                r = client.post(
                    "/setup/git/github/token",
                    json={"token": "bad"},
                )
                assert r.status_code == 401

            r = client.post(
                "/setup/git/github/token",
                json={"token": "gh_token"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["user"]["username"] == "octocat"

            r = client.get("/setup/git/github/repositories")
            assert r.status_code == 200
            data = r.get_json()["data"]
            # The repository without push permission is filtered out
            assert [repo["id"] for repo in data] == ["octocat/challenges"]

            r = client.post(
                "/setup/git/github/repositories",
                json={
                    "action": "select",
                    "repository": {
                        "id": "octocat/challenges",
                        "name": "octocat/challenges",
                        "default_branch": "main",
                    },
                },
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["repository"]["id"] == "octocat/challenges"
            # The missing sync workflow is only committed at setup completion,
            # after the secrets it needs exist
            assert data["ci_pending"] is True
            assert not any(
                method == "PUT" and "sync.yml" in url for method, url, _ in api.calls
            )

            r = client.get("/setup/git")
            assert r.get_json()["data"]["repository"]["id"] == "octocat/challenges"
    destroy_ctfd(app)


def test_git_github_select_invalid_project():
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)
        api = fake_api(
            [
                (("GET", "/user"), {"json": {"login": "octocat"}}),
                (("GET", "/contents/.ctf/config"), {"status": 404, "json": {}}),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            client.post(
                "/setup/git/github/token",
                json={"token": "gh_token"},
            )
            r = client.post(
                "/setup/git/github/repositories",
                json={
                    "action": "select",
                    "repository": {"id": "octocat/not-ctfcli"},
                },
            )
            assert r.status_code == 400
            assert "not a valid ctfcli project" in r.get_json()["errors"][0]
    destroy_ctfd(app)


def test_git_github_create_and_provision():
    from nacl import encoding, public

    public_key = (
        public.PrivateKey.generate()
        .public_key.encode(encoding.Base64Encoder())
        .decode()
    )
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)
        api = fake_api(
            [
                (("GET", "/user"), {"json": {"login": "octocat"}}),
                (
                    ("POST", "/user/repos"),
                    {
                        "status": 201,
                        "json": {
                            "full_name": "octocat/new-ctf",
                            "default_branch": "main",
                            "private": True,
                            "html_url": "https://github.com/octocat/new-ctf",
                        },
                    },
                ),
                (("PUT", "/contents/"), {"status": 201, "json": {}}),
                (
                    ("GET", "/actions/secrets/public-key"),
                    {"json": {"key_id": "1234", "key": public_key}},
                ),
                (("PUT", "/actions/secrets/"), {"status": 201, "json": {}}),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            client.post(
                "/setup/git/github/token",
                json={"token": "gh_token"},
            )
            r = client.post(
                "/setup/git/github/repositories",
                json={"action": "create", "name": "new-ctf"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["repository"]["id"] == "octocat/new-ctf"
            # Scaffold commits only .ctf/config and README.md; the workflow
            # file would trigger a run that fails without the secrets
            scaffolded = [
                url
                for method, url, _ in api.calls
                if method == "PUT" and "/contents/" in url
            ]
            assert len(scaffolded) == 2
            assert not any("sync.yml" in url for url in scaffolded)

            # Completing setup mints an access token and stores CI secrets
            with client.session_transaction() as sess:
                nonce = sess["nonce"]
            r = client.post(
                "/setup",
                data={
                    "ctf_name": "CTFd",
                    "ctf_description": "CTF description",
                    "name": "admin",
                    "email": "admin@examplectf.com",
                    "password": "password",
                    "user_mode": "users",
                    "nonce": nonce,
                },
            )
            assert r.status_code == 302

        secrets_set = [
            i
            for i, (method, url, _) in enumerate(api.calls)
            if method == "PUT" and "/actions/secrets/CTFCLI" in url
        ]
        assert len(secrets_set) == 2
        # The workflow file is committed only after both secrets are in place
        workflow_commits = [
            i
            for i, (method, url, _) in enumerate(api.calls)
            if method == "PUT" and "sync.yml" in url
        ]
        assert len(workflow_commits) == 1
        assert workflow_commits[0] > max(secrets_set)
        token = UserTokens.query.first()
        assert token is not None
        assert "ctfcli" in token.description
        assert get_config("git_provider") == "github"
        assert get_config("git_repository") == "octocat/new-ctf"
        assert get_config("git_token_id") == token.id
        with client.session_transaction() as sess:
            assert "setup_integration" not in sess
    destroy_ctfd(app)


def test_git_github_device_flow():
    app = create_ctfd(setup=False)
    app.config["GITHUB_CLIENT_ID"] = "test_client_id"
    with app.app_context():
        client = setup_client(app)
        api = fake_api(
            [
                (
                    ("POST", "/login/device/code"),
                    {
                        "json": {
                            "device_code": "devcode",
                            "user_code": "ABCD-1234",
                            "verification_uri": "https://github.com/login/device",
                            "interval": 5,
                            "expires_in": 900,
                        }
                    },
                ),
                (
                    ("POST", "/login/oauth/access_token"),
                    {"json": {"error": "authorization_pending"}},
                ),
                (("GET", "/user"), {"json": {"login": "octocat"}}),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            r = client.post("/setup/git/github/device", json={})
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["user_code"] == "ABCD-1234"
            # The device code stays server-side
            assert "device_code" not in data

            r = client.post("/setup/git/github/device/token", json={})
            assert r.get_json()["data"]["status"] == "pending"

        api = fake_api(
            [
                (
                    ("POST", "/login/oauth/access_token"),
                    {"json": {"access_token": "gh_device_token"}},
                ),
                (("GET", "/user"), {"json": {"login": "octocat"}}),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            r = client.post("/setup/git/github/device/token", json={})
            assert r.get_json()["data"]["status"] == "ok"
            assert r.get_json()["data"]["user"]["username"] == "octocat"
    destroy_ctfd(app)


def test_git_gitlab_token_select_and_create():
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)
        api = fake_api(
            [
                (("GET", "/api/v4/user"), {"json": {"username": "gitlabber"}}),
                (
                    ("GET", "/api/v4/projects?"),
                    {"json": []},  # unused fragment guard
                ),
                (
                    ("GET", "/api/v4/projects"),
                    {
                        "json": [
                            {
                                "id": 42,
                                "path_with_namespace": "gitlabber/challenges",
                                "default_branch": "main",
                                "visibility": "private",
                                "web_url": "https://gitlab.com/gitlabber/challenges",
                            }
                        ]
                    },
                ),
            ]
        )
        with patch(GITLAB_REQUESTS, side_effect=api):
            r = client.post(
                "/setup/git/gitlab/token",
                json={"token": "glpat"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["user"]["username"] == "gitlabber"

            r = client.get("/setup/git/gitlab/repositories")
            assert [repo["id"] for repo in r.get_json()["data"]] == [42]

        # Selecting a valid project that already has CI configured
        api = fake_api(
            [
                (("GET", "/repository/files/.ctf%2Fconfig"), {"json": {}}),
                (("GET", "/repository/files/.gitlab-ci.yml"), {"json": {}}),
            ]
        )
        with patch(GITLAB_REQUESTS, side_effect=api):
            r = client.post(
                "/setup/git/gitlab/repositories",
                json={
                    "action": "select",
                    "repository": {
                        "id": 42,
                        "name": "gitlabber/challenges",
                        "default_branch": "main",
                    },
                },
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["ci_pending"] is False

        # Creating a project scaffolds it with a single commit
        api = fake_api(
            [
                (
                    ("POST", "/api/v4/projects/43/repository/commits"),
                    {"status": 201, "json": {}},
                ),
                (
                    ("POST", "/api/v4/projects"),
                    {
                        "status": 201,
                        "json": {
                            "id": 43,
                            "path_with_namespace": "gitlabber/new-ctf",
                            "default_branch": None,
                            "visibility": "private",
                            "web_url": "https://gitlab.com/gitlabber/new-ctf",
                        },
                    },
                ),
            ]
        )
        with patch(GITLAB_REQUESTS, side_effect=api):
            r = client.post(
                "/setup/git/gitlab/repositories",
                json={"action": "create", "name": "new-ctf"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["repository"]["id"] == 43
            commit_calls = [
                kwargs
                for method, url, kwargs in api.calls
                if method == "POST" and "repository/commits" in url
            ]
            assert len(commit_calls) == 1
            paths = [
                action["file_path"] for action in commit_calls[0]["json"]["actions"]
            ]
            # .gitlab-ci.yml is deferred to setup completion so its pipeline
            # only runs once the CI variables exist
            assert paths == [".ctf/config", "README.md"]

        # Disconnect clears the session
        r = client.delete("/setup/git", json={})
        assert r.status_code == 200
        r = client.get("/setup/git/gitlab/repositories")
        assert r.status_code == 401
    destroy_ctfd(app)


def test_git_provider_settings():
    app = create_ctfd(setup=False)
    with app.app_context():
        client = setup_client(app)
        providers = client.get("/setup/git").get_json()["data"]["providers"]
        assert providers["github"]["name"] == "GitHub"
        assert providers["github"]["url"] == "https://github.com"
        assert providers["gitlab"]["name"] == "GitLab"
        assert providers["gitlab"]["url"] == "https://gitlab.com"
        # Device login is offered wherever a client ID is available
        assert providers["github"]["device"] is True
        app.config["GITLAB_CLIENT_ID"] = "gitlab_client_id"
        providers = client.get("/setup/git").get_json()["data"]["providers"]
        assert providers["gitlab"]["device"] is True
    destroy_ctfd(app)


def test_git_self_hosted_github():
    app = create_ctfd(setup=False)
    app.config["GITHUB_URL"] = "https://ghe.example.com/"
    with app.app_context():
        client = setup_client(app)
        # The bundled OAuth App only exists on github.com
        providers = client.get("/setup/git").get_json()["data"]["providers"]
        assert providers["github"] == {
            "name": "GitHub",
            "device": False,
            "url": "https://ghe.example.com",
        }
        r = client.post("/setup/git/github/device", json={})
        assert r.status_code == 400

        app.config["GITHUB_CLIENT_ID"] = "enterprise_client_id"
        api = fake_api(
            [
                (
                    ("POST", "/login/device/code"),
                    {
                        "json": {
                            "device_code": "devcode",
                            "user_code": "ABCD-1234",
                            "verification_uri": "https://ghe.example.com/login/device",
                        }
                    },
                ),
                (("GET", "/api/v3/user"), {"json": {"login": "octocat"}}),
                (
                    ("POST", "/login/oauth/access_token"),
                    {"json": {"access_token": "ghe_token"}},
                ),
            ]
        )
        with patch(GITHUB_REQUESTS, side_effect=api):
            r = client.post("/setup/git/github/device", json={})
            assert r.status_code == 200
            r = client.post("/setup/git/github/device/token", json={})
            assert r.get_json()["data"]["user"]["username"] == "octocat"

        # Every request goes to the self-hosted instance
        assert all(
            url.startswith("https://ghe.example.com/") for _, url, _ in api.calls
        )
    destroy_ctfd(app)
