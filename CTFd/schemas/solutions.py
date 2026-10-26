from CTFd.models import Solutions, ma
from CTFd.utils import string_types


class SolutionSchema(ma.ModelSchema):
    class Meta:
        model = Solutions
        include_fk = True
        dump_only = ("id",)

    views = {
        "locked": [
            "id",
            "challenge_id",
            "state",
        ],
        "unlocked": [
            "id",
            "challenge_id",
            "content",
            "html",
            "state",
        ],
        "admin": [
            "id",
            "challenge_id",
            "content",
            "html",
            "state",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to SolutionSchema as the view will be removed
                print(
                    "Passing a list of fields to SolutionSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(SolutionSchema, self).__init__(*args, **kwargs)
