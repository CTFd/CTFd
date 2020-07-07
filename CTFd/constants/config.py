import json

from CTFd.constants import JinjaEnum, RawEnum
from CTFd.utils import get_config


class ConfigTypes(str, RawEnum):
    CHALLENGE_VISIBILITY = "challenge_visibility"
    SCORE_VISIBILITY = "score_visibility"
    ACCOUNT_VISIBILITY = "account_visibility"
    REGISTRATION_VISIBILITY = "registration_visibility"


@JinjaEnum
class ChallengeVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    ADMINS = "admins"


@JinjaEnum
class ScoreVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    HIDDEN = "hidden"
    ADMINS = "admins"


@JinjaEnum
class AccountVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    ADMINS = "admins"


@JinjaEnum
class RegistrationVisibilityTypes(str, RawEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class _ConfigsWrapper:
    def __getattr__(self, attr):
        return get_config(attr)

    @property
    def ctf_name(self):
        return get_config("ctf_name", default="CTFd")

    @property
    def theme_header(self):
        from CTFd.utils.helpers import markup

        return markup(get_config("theme_header", default=""))

    @property
    def theme_footer(self):
        from CTFd.utils.helpers import markup

        return markup(get_config("theme_footer", default=""))

    @property
    def theme_settings(self):
        return json.loads(get_config("theme_settings", default="null"))


Configs = _ConfigsWrapper()
