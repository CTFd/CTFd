from CTFd.models import ModuleAudienceAccess, ModuleChallenges, Modules
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_audience,
    gen_challenge,
    gen_module,
    login_as_user,
    register_user,
)


def test_modules_list_admin_only():
    app = create_ctfd()
    with app.app_context():
        gen_module(app.db, name="owasp")
        register_user(app)
        json_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        with login_as_user(app) as client:
            r = client.get("/api/v1/modules", headers=json_headers)
            assert r.status_code == 403
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/modules", headers=json_headers)
            assert r.status_code == 200
            assert r.get_json()["data"][0]["name"] == "owasp"
    destroy_ctfd(app)


def test_modules_crud():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/modules", json={"name": "owasp"})
            assert r.status_code == 200
            module_id = r.get_json()["data"]["id"]
            assert Modules.query.count() == 1

            r = client.patch(
                "/api/v1/modules/{}".format(module_id), json={"name": "renamed"}
            )
            assert r.status_code == 200
            assert Modules.query.filter_by(id=module_id).first().name == "renamed"

            r = client.delete("/api/v1/modules/{}".format(module_id), json="")
            assert r.status_code == 200
            assert Modules.query.count() == 0
    destroy_ctfd(app)


def test_module_audience_link():
    app = create_ctfd()
    with app.app_context():
        audience_id = gen_audience(app.db, name="seceng").id
        module_id = gen_module(app.db, name="owasp").id
        register_user(app)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/modules/{}/audiences".format(module_id),
                json={"audience_id": audience_id},
            )
            assert r.status_code == 200
            assert ModuleAudienceAccess.query.count() == 1

            r = client.delete(
                "/api/v1/modules/{}/audiences/{}".format(module_id, audience_id),
                json="",
            )
            assert r.status_code == 200
            assert ModuleAudienceAccess.query.count() == 0
    destroy_ctfd(app)


def _module_ids_of(client, chal_id):
    r = client.get("/api/v1/challenges/{}".format(chal_id))
    return r.get_json()["data"]["module_ids"]


def test_challenge_module_ids_roundtrip():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        b = gen_module(app.db, name="b").id
        chal_id = gen_challenge(app.db, name="x", module_ids=[b, a]).id
        with login_as_user(app, name="admin") as client:
            assert _module_ids_of(client, chal_id) == [a, b]
            r = client.get("/api/v1/challenges?view=admin")
            item = next(c for c in r.get_json()["data"] if c["id"] == chal_id)
            assert item["module_ids"] == [a, b]
            assert "module_id" not in item
    destroy_ctfd(app)


def test_patch_module_ids():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        b = gen_module(app.db, name="b").id
        chal_id = gen_challenge(app.db, name="x", module_ids=[a]).id
        url = "/api/v1/challenges/{}".format(chal_id)
        with login_as_user(app, name="admin") as client:
            assert client.patch(url, json={"module_ids": [b, a, b]}).status_code == 200
            assert _module_ids_of(client, chal_id) == [a, b]

            client.patch(url, json={"name": "renamed"})
            assert _module_ids_of(client, chal_id) == [a, b]

            client.patch(url, json={"module_ids": None})
            assert _module_ids_of(client, chal_id) == []
    destroy_ctfd(app)


def test_patch_invalid_module_ids_is_400():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        chal_id = gen_challenge(app.db, name="x", module_ids=[a]).id
        url = "/api/v1/challenges/{}".format(chal_id)
        with login_as_user(app, name="admin") as client:
            for payload in ([a, 999], ["x", 999], [None, 999]):
                r = client.patch(url, json={"module_ids": payload})
                assert r.status_code == 400
                assert list(r.get_json()["errors"]) == ["module_ids"]
            assert _module_ids_of(client, chal_id) == [a]
    destroy_ctfd(app)


def test_create_challenge_with_module_ids():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/challenges",
                json={
                    "name": "x",
                    "category": "cat",
                    "description": "desc",
                    "value": 100,
                    "state": "visible",
                    "type": "standard",
                    "module_ids": [a],
                },
            )
            assert r.status_code == 200
            assert _module_ids_of(client, r.get_json()["data"]["id"]) == [a]
    destroy_ctfd(app)


def test_module_challenge_link_and_unlink():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        b = gen_module(app.db, name="b").id
        chal_id = gen_challenge(app.db, name="x", module_ids=[a]).id
        unlink_url = "/api/v1/modules/{}/challenges/{}".format(a, chal_id)
        with login_as_user(app, name="admin") as client:
            for _ in range(2):
                r = client.post(
                    "/api/v1/modules/{}/challenges".format(b),
                    json={"challenge_id": chal_id},
                )
                assert r.status_code == 200
            assert _module_ids_of(client, chal_id) == [a, b]
            assert ModuleChallenges.query.filter_by(module_id=b).count() == 1

            assert client.delete(unlink_url, json="").status_code == 200
            assert _module_ids_of(client, chal_id) == [b]
            assert client.delete(unlink_url, json="").status_code == 404
    destroy_ctfd(app)


def test_module_delete_keeps_other_links():
    app = create_ctfd()
    with app.app_context():
        a = gen_module(app.db, name="a").id
        b = gen_module(app.db, name="b").id
        shared_id = gen_challenge(app.db, name="shared", module_ids=[a, b]).id
        only_a_id = gen_challenge(app.db, name="only_a", module_ids=[a]).id
        register_user(app)
        with login_as_user(app, name="admin") as client:
            client.delete("/api/v1/modules/{}".format(a), json="")
            assert _module_ids_of(client, shared_id) == [b]
        with login_as_user(app) as client:
            ids = {c["id"] for c in client.get("/api/v1/challenges").get_json()["data"]}
            assert shared_id not in ids
            assert only_a_id in ids
    destroy_ctfd(app)
