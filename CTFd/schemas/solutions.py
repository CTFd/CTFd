from marshmallow import fields

from CTFd.models import Solutions, ma
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.utils import string_types


class SolutionSchema(ma.ModelSchema):
    class Meta:
        model = Solutions
        include_fk = True
        dump_only = ("id",)
        # Don't include the challenge field in response as by default it is the same as challenge_id
        exclude = ("challenge",)

    views = {
        "admin": [
            "id",
            "challenge_id",
            "challenge",
            "content",
            "state",
        ],
        "user": [
            "id",
            "challenge_id",
            "challenge",
            "content",
            "state",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(SolutionSchema, self).__init__(*args, **kwargs)
