from markupsafe import Markup

from CTFd.utils import get_config


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
