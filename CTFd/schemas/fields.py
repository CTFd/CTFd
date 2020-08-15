from marshmallow import fields, pre_load

from CTFd.models import FieldEntries, Fields, db, ma
from CTFd.utils.user import get_current_user, is_admin


class FieldSchema(ma.ModelSchema):
    class Meta:
        model = Fields
        include_fk = True
        dump_only = ("id",)


class FieldEntriesSchema(ma.ModelSchema):
    class Meta:
        model = FieldEntries
        include_fk = True
        load_only = ("id", )
        exclude = ("field", "user", "user_id")
        dump_only = ("user_id", "name", "description", "type")

    name = fields.Nested(FieldSchema, only=("name"), attribute="field")
    description = fields.Nested(FieldSchema, only=("description"), attribute="field")
    type = fields.Nested(FieldSchema, only=("field_type"), attribute="field")
