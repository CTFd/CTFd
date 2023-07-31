from CTFd.models import Unlocks
from CTFd.schemas import ma

from CTFd.utils import string_types


class UnlockSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Unlocks
        include_fk = True
        dump_only = ("id", "date")
        load_instance = True

    views = {
        "admin": ["user_id", "target", "team_id", "date", "type", "id"],
        "user": ["target", "date", "type", "id"],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(UnlockSchema, self).__init__(*args, **kwargs)
