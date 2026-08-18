from urllib.parse import quote

import requests

from CTFd.utils.git.provider import (
    GITLAB_CI,
    GITLAB_CI_PATH,
    BaseProvider,
    GitError,
)

DEFAULT_GITLAB_URL = "https://gitlab.com"
DEVICE_FLOW_SCOPE = "api"

# TODO: Application ID of the shared OAuth application used for device flow
# login on gitlab.com. Until it is filled in, device login is only available
# to deployments that set GITLAB_CLIENT_ID themselves.
DEFAULT_CLIENT_ID = "9ef448df1f0b6ebf1eca6d967ee13a1b05a1432683e057a19503093642d9cf2f"


class GitLabProvider(BaseProvider):
    id = "gitlab"
    name = "GitLab"
    ci_path = GITLAB_CI_PATH
    ci_file = GITLAB_CI
    default_url = DEFAULT_GITLAB_URL
    default_client_id = DEFAULT_CLIENT_ID

    @property
    def api_url(self):
        return f"{self.url}/api/v4"

    def _request(self, method, url, token=None, **kwargs):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            return requests.request(method, url, headers=headers, timeout=10, **kwargs)
        except requests.RequestException:
            raise GitError("Could not reach GitLab", status_code=502)

    def device_authorization(self):
        client_id = self.client_id
        if not client_id:
            raise GitError("GitLab device login is not configured on this instance")

        r = self._request(
            "POST",
            f"{self.url}/oauth/authorize_device",
            data={"client_id": client_id, "scope": DEVICE_FLOW_SCOPE},
        )
        if r.status_code != 200 or "device_code" not in r.json():
            raise GitError("Could not start GitLab device login")

        data = r.json()
        return {
            "device_code": data["device_code"],
            "user_code": data["user_code"],
            "verification_uri": data.get("verification_uri_complete")
            or data["verification_uri"],
            "interval": data.get("interval", 5),
            "expires_in": data.get("expires_in", 300),
        }

    def device_token(self, device_code):
        r = self._request(
            "POST",
            f"{self.url}/oauth/token",
            data={
                "client_id": self.client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )

        data = (
            r.json()
            if r.headers.get("content-type", "").startswith("application/json")
            else {}
        )
        if r.status_code == 200 and data.get("access_token"):
            return {"status": "ok", "token": data["access_token"]}

        error = data.get("error", "unknown_error")
        if error in ("authorization_pending", "slow_down"):
            return {"status": "pending"}

        return {
            "status": "error",
            "message": data.get("error_description", "GitLab device login failed"),
        }

    def get_user(self, token):
        r = self._request("GET", f"{self.api_url}/user", token=token)
        if r.status_code != 200:
            raise GitError("GitLab token is invalid", status_code=401)
        return {"username": r.json()["username"]}

    def list_repositories(self, token):
        r = self._request(
            "GET",
            f"{self.api_url}/projects",
            token=token,
            params={
                "membership": True,
                # Developer role and above can push
                "min_access_level": 30,
                "order_by": "last_activity_at",
                "per_page": 100,
            },
        )
        if r.status_code != 200:
            raise GitError("Could not list GitLab projects")

        return [self._repo(project) for project in r.json()]

    def _repo(self, data):
        return {
            "id": data["id"],
            "name": data["path_with_namespace"],
            "default_branch": data.get("default_branch") or "main",
            "private": data.get("visibility", "private") != "public",
            "url": data.get("web_url"),
        }

    def has_file(self, token, repo, path):
        encoded = quote(path, safe="")
        r = self._request(
            "GET",
            f"{self.api_url}/projects/{repo['id']}/repository/files/{encoded}",
            token=token,
            params={"ref": repo["default_branch"]},
        )
        return r.status_code == 200

    def create_repository(self, token, name, private=True):
        r = self._request(
            "POST",
            f"{self.api_url}/projects",
            token=token,
            json={
                "name": name,
                "visibility": "private" if private else "public",
                "initialize_with_readme": False,
                "description": "CTFd challenge repository managed with ctfcli",
            },
        )
        if r.status_code != 201:
            message = None
            try:
                message = str(r.json().get("message"))
            except ValueError:
                pass
            raise GitError(message or "Could not create GitLab project")

        return self._repo(r.json())

    def create_files(self, token, repo, files, message):
        r = self._request(
            "POST",
            f"{self.api_url}/projects/{repo['id']}/repository/commits",
            token=token,
            json={
                "branch": repo["default_branch"],
                "commit_message": message,
                "actions": [
                    {"action": "create", "file_path": path, "content": content}
                    for path, content in files.items()
                ],
            },
        )
        if r.status_code != 201:
            raise GitError("Could not commit to GitLab project")

    def provision_credentials(self, token, repo, ctfd_url, ctfd_token):
        for key, value, masked in (
            ("CTFCLI_URL", ctfd_url, False),
            ("CTFCLI_ACCESS_TOKEN", ctfd_token, True),
        ):
            payload = {
                "key": key,
                "value": value,
                "masked": masked,
                "protected": False,
            }

            r = self._request(
                "POST",
                f"{self.api_url}/projects/{repo['id']}/variables",
                token=token,
                json=payload,
            )
            if r.status_code == 400:
                r = self._request(
                    "PUT",
                    f"{self.api_url}/projects/{repo['id']}/variables/{key}",
                    token=token,
                    json=payload,
                )

            if r.status_code not in (200, 201):
                raise GitError(f"Could not set GitLab CI variable {key}")
