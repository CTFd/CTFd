from CTFd.models import Tags
from CTFd.schemas import ma

from CTFd.utils import string_types


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tags
        include_fk = True
        dump_only = ("id",)
        load_instance = True

    views = {"admin": ["id", "challenge", "value"], "user": ["value"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TagSchema, self).__init__(*args, **kwargs)
