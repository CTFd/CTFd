from dataclasses import dataclass
from CTFd.utils import get_config
from markupsafe import Markup


class _ConfigsWrapper:
    def __getattr__(self, attr):
        return get_config(attr)

    @property
    def theme_header(self):
        return Markup(get_config("theme_header", default=""))

    @property
    def theme_footer(self):
        return Markup(get_config("theme_footer", default=""))


Configs = _ConfigsWrapper()
