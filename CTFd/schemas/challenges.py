from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load, validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Challenges


class ChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        include_fk = True
        dump_only = ('id',)
