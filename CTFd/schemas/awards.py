from CTFd.models import Awards, ma
from CTFd.utils import string_types


class AwardSchema(ma.ModelSchema):
    class Meta:
        model = Awards
        include_fk = True
        dump_only = ("id", "date")

    views = {
        "admin": [
            "category",
            "user_id",
            "name",
            "description",
            "value",
            "team_id",
            "user",
            "team",
            "date",
            "requirements",
            "id",
            "icon",
        ],
        "user": [
            "category",
            "user_id",
            "name",
            "description",
            "value",
            "team_id",
            "user",
            "team",
            "date",
            "id",
            "icon",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to AwardSchema as the view will be removed
                print(
                    "Passing a list of fields to AwardSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(AwardSchema, self).__init__(*args, **kwargs)
