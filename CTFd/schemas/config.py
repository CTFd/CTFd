from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy import field_for

from CTFd.models import Configs, ma
from CTFd.utils import string_types


class ConfigValueField(fields.Field):
    """
    Custom value field for Configs so that we can perform validation of values
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            # 65535 bytes is the size of a TEXT column in MySQL
            # You may be able to exceed this in other databases
            # but MySQL is our database of record
            if len(value) > 65535:
                raise ValidationError(f'{data["key"]} config is too long')
            return value
        else:
            return value


class ConfigSchema(ma.ModelSchema):
    class Meta:
        model = Configs
        include_fk = True
        dump_only = ("id",)

    views = {"admin": ["id", "key", "value"]}
    key = field_for(Configs, "key", required=True)
    value = ConfigValueField(allow_none=True, required=True)

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(ConfigSchema, self).__init__(*args, **kwargs)
