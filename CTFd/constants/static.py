from CTFd.constants import JinjaEnum, RawEnum


@JinjaEnum
class CacheKeys(str, RawEnum):
    PUBLIC_SCOREBOARD_TABLE = "public_scoreboard_table"


# Placeholder object. Not used, just imported to force initialization of any Enums here
class _StaticsWrapper:
    pass


Static = _StaticsWrapper()
