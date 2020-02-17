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
                kwargs["only"] = view

        super(AwardSchema, self).__init__(*args, **kwargs)
