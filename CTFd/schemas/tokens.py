from CTFd.models import Tokens
from CTFd.schemas import ma

from CTFd.utils import string_types


class TokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tokens
        include_fk = True
        dump_only = ("id", "expiration", "type")
        load_instance = True

    views = {
        "admin": [
            "id",
            "type",
            "user_id",
            "created",
            "expiration",
            "description",
            "value",
        ],
        "user": ["id", "type", "created", "expiration", "description"],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TokenSchema, self).__init__(*args, **kwargs)
