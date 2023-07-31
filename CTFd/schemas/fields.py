from marshmallow import fields

from CTFd.models import Fields, TeamFieldEntries, UserFieldEntries, db
from CTFd.schemas import ma


class FieldSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fields
        include_fk = True
        dump_only = ("id",)


class UserFieldEntriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserFieldEntries
        sqla_session = db.session
        include_fk = True
        load_only = ("id",)
        exclude = ("field", "user", "user_id")
        dump_only = ("user_id", "name", "description", "type")
        load_instance = True

    name = fields.Nested(FieldSchema, only=("name",), attribute="field")
    description = fields.Nested(FieldSchema, only=("description",), attribute="field")
    type = fields.Nested(FieldSchema, only=("field_type",), attribute="field")


class TeamFieldEntriesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TeamFieldEntries
        sqla_session = db.session
        include_fk = True
        load_only = ("id",)
        exclude = ("field", "team", "team_id")
        dump_only = ("team_id", "name", "description", "type")

    name = fields.Nested(FieldSchema, only=("name",), attribute="field")
    description = fields.Nested(FieldSchema, only=("description",), attribute="field")
    type = fields.Nested(FieldSchema, only=("field_type",), attribute="field")
