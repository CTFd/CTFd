from marshmallow import fields

from CTFd.models import Comments
from CTFd.schemas import ma

from CTFd.schemas.users import UserSchema


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comments
        include_fk = True
        dump_only = ("id", "date", "html", "author", "author_id", "type")
        load_instance = True

    author = fields.Nested(UserSchema(only=("name",)))
    html = fields.String()
