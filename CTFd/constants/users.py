from collections import namedtuple

UserAttrs = namedtuple(
    "UserAttrs",
    [
        "id",
        "oauth_id",
        "name",
        "email",
        "type",
        "secret",
        "website",
        "affiliation",
        "country",
        "bracket",
        "hidden",
        "banned",
        "verified",
        "team_id",
        "created",
    ],
)


class _UserAttrsWrapper:
    def __getattr__(self, attr):
        from CTFd.utils.user import get_current_user_attrs

        attrs = get_current_user_attrs()
        return getattr(attrs, attr, None)

    @property
    def place(self):
        from CTFd.utils.user import get_current_user

        user = get_current_user()
        if user:
            return user.place
        return None

    @property
    def score(self):
        from CTFd.utils.user import get_current_user

        user = get_current_user()
        if user:
            return user.score
        return None


User = _UserAttrsWrapper()
