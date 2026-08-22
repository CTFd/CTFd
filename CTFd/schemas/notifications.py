from marshmallow import fields

from CTFd.models import Notifications, ma
from CTFd.utils import string_types


class NotificationSchema(ma.ModelSchema):
    class Meta:
        model = Notifications
        include_fk = True
        dump_only = ("id", "date", "html")

    # Used to force the schema to include the html property from the model
    html = fields.Str()

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to NotificationSchema as the view will be removed
                print(
                    "Passing a list of fields to NotificationSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(NotificationSchema, self).__init__(*args, **kwargs)
