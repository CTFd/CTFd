from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.hash import bcrypt_sha256
from sqlalchemy import TypeDecorator, String, func, types, CheckConstraint, and_
from sqlalchemy.sql.expression import union_all
from sqlalchemy.types import JSON, NullType
from sqlalchemy.orm import validates, column_property
from CTFd.utils.crypto import hash_password
import datetime
import json

db = SQLAlchemy()
ma = Marshmallow()

class SQLiteJson(TypeDecorator):
    impl = String

    class Comparator(String.Comparator):
        def __getitem__(self, index):
            if isinstance(index, tuple):
                index = "$%s" % (
                    "".join([
                        "[%s]" % elem if isinstance(elem, int)
                        else '."%s"' % elem for elem in index
                    ])
                )
            elif isinstance(index, int):
                index = "$[%s]" % index
            else:
                index = '$."%s"' % index

            # json_extract does not appear to return JSON sub-elements
            # which is weird.
            return func.json_extract(self.expr, index, type_=NullType)

    comparator_factory = Comparator

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


JSONLite = types.JSON().with_variant(SQLiteJson, 'sqlite')

from CTFd.models.config import Config
from CTFd.models.files import Files, ChallengeFiles, PageFiles
from CTFd.models.tags import Tags
from CTFd.models.hints import Hints
from CTFd.models.challenges import Challenges
from CTFd.models.users import Users, Admins
from CTFd.models.teams import Teams
from CTFd.models.flags import Flags
from CTFd.models.announcements import Announcements
from CTFd.models.awards import Awards
from CTFd.models.pages import Pages
from CTFd.models.submissions import Submissions, Solves, Fails
from CTFd.models.tracking import Tracking
from CTFd.models.unlocks import Unlocks, AwardUnlocks, ChallengesUnlocks, HintUnlocks

