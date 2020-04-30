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
