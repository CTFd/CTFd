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
