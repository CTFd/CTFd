from CTFd.models import Flags
from CTFd.schemas import ma

from CTFd.utils import string_types


class FlagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Flags
        include_fk = True
        dump_only = ("id",)
        load_instance = True

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(FlagSchema, self).__init__(*args, **kwargs)
