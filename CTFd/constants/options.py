from CTFd.constants import JinjaEnum, RawEnum


class ConfigTypes(str, RawEnum):
    CHALLENGE_VISIBILITY = "challenge_visibility"
    SCORE_VISIBILITY = "score_visibility"
    ACCOUNT_VISIBILITY = "account_visibility"
    REGISTRATION_VISIBILITY = "registration_visibility"


@JinjaEnum
class UserModeTypes(str, RawEnum):
    USERS = "users"
    TEAMS = "teams"


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
    MLC = "mlc"
