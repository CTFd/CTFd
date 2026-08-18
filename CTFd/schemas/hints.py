from CTFd.models import Hints, ma
from CTFd.utils import string_types


class HintSchema(ma.ModelSchema):
    class Meta:
        model = Hints
        include_fk = True
        dump_only = ("id", "type", "html")

    views = {
        "locked": ["id", "title", "type", "challenge", "challenge_id", "cost"],
        "unlocked": [
            "id",
            "title",
            "type",
            "challenge",
            "challenge_id",
            "content",
            "html",
            "cost",
        ],
        "admin": [
            "id",
            "title",
            "type",
            "challenge",
            "challenge_id",
            "content",
            "html",
            "cost",
            "requirements",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to HintSchema as the view will be removed
                print(
                    "Passing a list of fields to HintSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(HintSchema, self).__init__(*args, **kwargs)
