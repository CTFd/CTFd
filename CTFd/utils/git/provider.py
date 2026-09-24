from CTFd.utils import get_app_config, get_config

# Pinned so a ctfcli release cannot break already provisioned pipelines
CTFCLI_VERSION = "0.1.8"

GITHUB_WORKFLOW_PATH = ".github/workflows/sync.yml"

# %-formatted to avoid escaping github ${{ }} syntax
GITHUB_WORKFLOW = """name: Sync challenges to CTFd

on:
  push:
    branches:
      - main
      - master
  workflow_dispatch:

jobs:
  sync:
    if: github.ref == format('refs/heads/{0}', github.event.repository.default_branch)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Install ctfcli
        run: pip install ctfcli==%(version)s

      - name: Sync challenges to CTFd
        run: ctf challenge install --force
        env:
          CTFCLI_URL: ${{ secrets.CTFCLI_URL }}
          CTFCLI_ACCESS_TOKEN: ${{ secrets.CTFCLI_ACCESS_TOKEN }}
""" % {"version": CTFCLI_VERSION}


GITLAB_CI_PATH = ".gitlab-ci.yml"
GITLAB_CI = f"""sync-challenges:
  image: python:3
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - pip install ctfcli=={CTFCLI_VERSION}
    - ctf challenge install --force
"""

CTFCLI_CONFIG_PATH = ".ctf/config"
CTFCLI_CONFIG = """[config]
url = {ctfd_url}
# The access token is deliberately not committed to the repository.
# For local use, add an `access_token` key here or set the
# CTFCLI_ACCESS_TOKEN environment variable.

[challenges]
"""

SCAFFOLD_README = """# {name}

This repository is a [ctfcli](https://github.com/CTFd/ctfcli) project holding
the challenges for the CTFd instance at {ctfd_url}.

Challenges pushed to the default branch are synced to CTFd automatically by
the bundled CI pipeline.

## Getting started

```
pip install ctfcli
git clone <this repository>
ctf challenge new mychallenge
# edit mychallenge/challenge.yml, then register it:
ctf challenge add mychallenge
git add . && git commit -m "Add mychallenge" && git push
```

To work against the CTFd instance locally, set the CTFCLI_ACCESS_TOKEN
environment variable to an admin access token (Settings -> Access Tokens).
"""


class GitError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def ctfcli_scaffold(repo, ctfd_url):
    """Files that turn an empty repository into a ctfcli project."""
    return {
        CTFCLI_CONFIG_PATH: CTFCLI_CONFIG.format(ctfd_url=ctfd_url),
        "README.md": SCAFFOLD_README.format(name=repo["name"], ctfd_url=ctfd_url),
    }


class BaseProvider:
    id = None
    name = None
    # Path and content of the provider's challenge sync pipeline file
    ci_path = None
    ci_file = None
    # URL of the provider's hosted instance and the client ID of the OAuth
    # app CTFd ships for it. Self-hosted instances get neither by default.
    default_url = None
    default_client_id = None

    def config(self, key, default=None):
        # App config (config.ini / env) takes precedence over DB config
        value = get_app_config(key)
        if not value:
            value = get_config(key.lower())

        return value if value else default

    # Properties are deliberately not cached: providers are module-level
    # singletons that outlive app instances, and these derive from config.
    @property
    def url(self):
        return self.config(f"{self.id.upper()}_URL", default=self.default_url).rstrip(
            "/"
        )

    @property
    def api_url(self):
        raise NotImplementedError

    @property
    def client_id(self):
        default = self.default_client_id if self.url == self.default_url else None
        return self.config(f"{self.id.upper()}_CLIENT_ID", default=default)

    @property
    def device_enabled(self):
        return bool(self.client_id)

    @property
    def settings(self):
        return {"name": self.name, "device": self.device_enabled, "url": self.url}

    # Every method below operates with a user-supplied or device-flow token.
    def device_authorization(self):
        raise NotImplementedError

    def device_token(self, device_code):
        raise NotImplementedError

    def get_user(self, token):
        raise NotImplementedError

    def list_repositories(self, token):
        raise NotImplementedError

    def create_repository(self, token, name, private=True):
        raise NotImplementedError

    def has_file(self, token, repo, path):
        raise NotImplementedError

    def create_files(self, token, repo, files, message):
        """Commit ``files`` ({path: content}) to the repo's default branch."""
        raise NotImplementedError

    def provision_credentials(self, token, repo, ctfd_url, ctfd_token):
        raise NotImplementedError
