from base64 import b64encode

import requests
from nacl import encoding, public

from CTFd.utils.git.provider import (
    GITHUB_WORKFLOW,
    GITHUB_WORKFLOW_PATH,
    BaseProvider,
    GitError,
)

DEFAULT_GITHUB_URL = "https://github.com"
GITHUB_API_URL = "https://api.github.com"

# repo: read/write repository contents & secrets, workflow: push workflow files
DEVICE_FLOW_SCOPE = "repo workflow"

# Client ID of the shared OAuth App used for device flow login on github.com.
# Deployments can override it with the GITHUB_CLIENT_ID setting
# to present their own app on the consent screen.
DEFAULT_CLIENT_ID = "Ov23lil6V94Ab0t0JCWD"


class GitHubProvider(BaseProvider):
    id = "github"
    name = "GitHub"
    ci_path = GITHUB_WORKFLOW_PATH
    ci_file = GITHUB_WORKFLOW
    default_url = DEFAULT_GITHUB_URL
    default_client_id = DEFAULT_CLIENT_ID

    @property
    def api_url(self):
        # GitHub Enterprise Server serves the API under /api/v3
        if self.url == DEFAULT_GITHUB_URL:
            return GITHUB_API_URL
        return f"{self.url}/api/v3"

    def _headers(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method, url, token=None, **kwargs):
        headers = kwargs.pop("headers", None) or (
            self._headers(token) if token else {"Accept": "application/json"}
        )
        try:
            return requests.request(method, url, headers=headers, timeout=10, **kwargs)
        except requests.RequestException:
            raise GitError("Could not reach GitHub", status_code=502)

    def device_authorization(self):
        client_id = self.client_id
        if not client_id:
            raise GitError("GitHub device login is not configured on this instance")

        r = self._request(
            "POST",
            f"{self.url}/login/device/code",
            data={"client_id": client_id, "scope": DEVICE_FLOW_SCOPE},
        )
        if r.status_code != 200 or "device_code" not in r.json():
            raise GitError("Could not start GitHub device login")

        data = r.json()
        return {
            "device_code": data["device_code"],
            "user_code": data["user_code"],
            "verification_uri": data["verification_uri"],
            "interval": data.get("interval", 5),
            "expires_in": data.get("expires_in", 900),
        }

    def device_token(self, device_code):
        r = self._request(
            "POST",
            f"{self.url}/login/oauth/access_token",
            data={
                "client_id": self.client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )

        data = r.json() if r.status_code == 200 else {}
        if data.get("access_token"):
            return {"status": "ok", "token": data["access_token"]}

        error = data.get("error", "unknown_error")
        if error in ("authorization_pending", "slow_down"):
            return {"status": "pending"}

        return {
            "status": "error",
            "message": data.get("error_description", "GitHub device login failed"),
        }

    def get_user(self, token):
        r = self._request("GET", f"{self.api_url}/user", token=token)
        if r.status_code != 200:
            raise GitError("GitHub token is invalid", status_code=401)
        return {"username": r.json()["login"]}

    def list_repositories(self, token):
        r = self._request(
            "GET",
            f"{self.api_url}/user/repos",
            token=token,
            params={"per_page": 100, "sort": "pushed"},
        )
        if r.status_code != 200:
            raise GitError("Could not list GitHub repositories")

        repos = []
        for repo in r.json():
            if repo.get("permissions", {}).get("push") is False:
                continue
            repos.append(self._repo(repo))

        return repos

    def _repo(self, data):
        return {
            "id": data["full_name"],
            "name": data["full_name"],
            "default_branch": data.get("default_branch") or "main",
            "private": data.get("private", True),
            "url": data.get("html_url"),
        }

    def has_file(self, token, repo, path):
        r = self._request(
            "GET",
            f"{self.api_url}/repos/{repo['id']}/contents/{path}",
            token=token,
        )
        return r.status_code == 200

    def create_repository(self, token, name, private=True):
        r = self._request(
            "POST",
            f"{self.api_url}/user/repos",
            token=token,
            json={
                "name": name,
                "private": private,
                "auto_init": False,
                "description": "CTFd challenge repository managed with ctfcli",
            },
        )
        if r.status_code != 201:
            errors = r.json().get("errors") if r.status_code == 422 else None
            message = errors[0].get("message") if errors else None
            raise GitError(message or "Could not create GitHub repository")

        return self._repo(r.json())

    def create_files(self, token, repo, files, message):
        for path, content in files.items():
            r = self._request(
                "PUT",
                f"{self.api_url}/repos/{repo['id']}/contents/{path}",
                token=token,
                json={
                    "message": message,
                    "content": b64encode(content.encode()).decode(),
                },
            )
            if r.status_code not in (200, 201):
                raise GitError(f"Could not commit {path} to GitHub repository")

    def _encrypt_secret(self, public_key, value):
        key = public.PublicKey(public_key.encode(), encoding.Base64Encoder())
        sealed_box = public.SealedBox(key)
        return b64encode(sealed_box.encrypt(value.encode())).decode()

    def provision_credentials(self, token, repo, ctfd_url, ctfd_token):
        r = self._request(
            "GET",
            f"{self.api_url}/repos/{repo['id']}/actions/secrets/public-key",
            token=token,
        )
        if r.status_code != 200:
            raise GitError("Could not fetch GitHub repository public key")

        key = r.json()
        for name, value in (
            ("CTFCLI_URL", ctfd_url),
            ("CTFCLI_ACCESS_TOKEN", ctfd_token),
        ):
            r = self._request(
                "PUT",
                f"{self.api_url}/repos/{repo['id']}/actions/secrets/{name}",
                token=token,
                json={
                    "encrypted_value": self._encrypt_secret(key["key"], value),
                    "key_id": key["key_id"],
                },
            )
            if r.status_code not in (201, 204):
                raise GitError(f"Could not set GitHub secret {name}")
