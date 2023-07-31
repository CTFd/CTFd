from marshmallow import fields

from CTFd.models import Notifications
from CTFd.schemas import ma

from CTFd.utils import string_types


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notifications
        include_fk = True
        dump_only = ("id", "date", "html")
        load_instance = True

    # Used to force the schema to include the html property from the model
    html = fields.Str()

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(NotificationSchema, self).__init__(*args, **kwargs)
