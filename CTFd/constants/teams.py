from collections import namedtuple

TeamAttrs = namedtuple(
    "TeamAttrs",
    [
        "id",
        "oauth_id",
        "name",
        "email",
        "secret",
        "website",
        "affiliation",
        "country",
        "bracket",
        "hidden",
        "banned",
        "captain_id",
        "created",
    ],
)


class _TeamAttrsWrapper:
    def __getattr__(self, attr):
        from CTFd.utils.user import get_current_team_attrs

        attrs = get_current_team_attrs()
        return getattr(attrs, attr, None)

    @property
    def place(self):
        from CTFd.utils.user import get_current_team

        team = get_current_team()
        if team:
            return team.place
        return None

    @property
    def score(self):
        from CTFd.utils.user import get_current_team

        team = get_current_team()
        if team:
            return team.score
        return None


Team = _TeamAttrsWrapper()
