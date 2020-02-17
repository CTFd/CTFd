from CTFd.models import Tokens, ma
from CTFd.utils import string_types


class TokenSchema(ma.ModelSchema):
    class Meta:
        model = Tokens
        include_fk = True
        dump_only = ("id", "expiration", "type")

    views = {
        "admin": ["id", "type", "user_id", "created", "expiration", "value"],
        "user": ["id", "type", "created", "expiration"],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TokenSchema, self).__init__(*args, **kwargs)
