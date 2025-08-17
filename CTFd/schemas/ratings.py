from marshmallow import fields

from CTFd.models import Ratings, ma
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.users import UserSchema
from CTFd.utils import string_types


class RatingSchema(ma.ModelSchema):
    user = fields.Nested(UserSchema, only=["id", "name"])
    challenge = fields.Nested(ChallengeSchema, only=["id", "name", "category"])

    class Meta:
        model = Ratings
        include_fk = True
        dump_only = ("id", "date", "user_id", "challenge_id")

    views = {
        "admin": [
            "id",
            "user_id",
            "user",
            "challenge_id",
            "challenge",
            "value",
            "review",
            "date",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(RatingSchema, self).__init__(*args, **kwargs)
