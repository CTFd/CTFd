from CTFd.utils import get_config
from CTFd.utils.git import PROVIDERS


class _GitWrapper:
    @property
    def providers(self):
        return {pid: provider.settings for pid, provider in PROVIDERS.items()}

    @property
    def provider(self):
        return get_config("git_provider")

    @property
    def repository(self):
        return get_config("git_repository")


Git = _GitWrapper()
