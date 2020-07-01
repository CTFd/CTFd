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
        from CTFd.utils.user import get_user_place

        return get_user_place(user_id=self.id)

    @property
    def score(self):
        from CTFd.utils.user import get_user_score

        return get_user_score(user_id=self.id)


User = _UserAttrsWrapper()
