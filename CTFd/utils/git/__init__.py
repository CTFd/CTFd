from CTFd.utils.git.github import GitHubProvider
from CTFd.utils.git.gitlab import GitLabProvider
from CTFd.utils.git.provider import (  # noqa: F401
    CTFCLI_CONFIG_PATH,
    GitError,
    ctfcli_scaffold,
)

PROVIDERS = {
    GitHubProvider.id: GitHubProvider(),
    GitLabProvider.id: GitLabProvider(),
}


def get_provider(name):
    provider = PROVIDERS.get(name)
    if provider is None:
        raise GitError(f"Unknown git provider: {name}", status_code=404)
    return provider
