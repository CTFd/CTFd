from CTFd.models import Solutions, ma
from CTFd.utils import string_types


class SolutionSchema(ma.ModelSchema):
    class Meta:
        model = Solutions
        include_fk = True
        dump_only = ("id",)

    views = {
        "admin": [
            "id",
            "content",
            "html",
            "state",
        ],
        "user": [
            "id",
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
                kwargs["only"] = view

        super(SolutionSchema, self).__init__(*args, **kwargs)
