from marshmallow import fields
from CTFd.models import ma
from CTFd.plugins.csaw.models import CSAWMembers


class CSAWMembersSchema(ma.Schema):
    user_id = fields.Integer()
    name = fields.Str()
    email = fields.Email()
    school = fields.Str()
