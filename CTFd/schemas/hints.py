from CTFd.models import Hints, ma
from CTFd.utils import string_types


class HintSchema(ma.ModelSchema):
    class Meta:
        model = Hints
        include_fk = True
        dump_only = ("id", "type", "html")

    views = {
        "locked": ["id", "type", "challenge", "cost"],
        "unlocked": ["id", "type", "challenge", "content", "html", "cost"],
        "admin": ["id", "type", "challenge", "content", "html", "cost", "requirements"],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(HintSchema, self).__init__(*args, **kwargs)
