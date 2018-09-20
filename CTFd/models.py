from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt_sha256
from sqlalchemy import TypeDecorator, String, func, types, CheckConstraint, and_
from sqlalchemy.sql.expression import union_all
from sqlalchemy.types import JSON, NullType
from sqlalchemy.orm import validates, column_property
from CTFd.utils.crypto import hash_password
import datetime
import json

db = SQLAlchemy()


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


class Announcements(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, content):
        self.content = content


class Pages(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    auth_required = db.Column(db.Boolean)
    title = db.Column(db.String(80))
    route = db.Column(db.Text, unique=True)
    html = db.Column(db.Text)
    draft = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    # TODO: Use hidden attribute

    files = db.relationship("PageFiles", backref="page")

    def __init__(self, title, route, html, draft=True, auth_required=False):
        self.title = title
        self.route = route
        self.html = html
        self.draft = draft
        self.auth_required = auth_required

    def __repr__(self):
        return "<Pages {0}>".format(self.route)


class Challenges(db.Model):
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=0)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    type = db.Column(db.String(80))
    hidden = db.Column(db.Boolean)
    requirements = db.Column(JSONLite)

    files = db.relationship("ChallengeFiles", backref="challenge")
    tags = db.relationship("Tags", backref="challenge")
    hints = db.relationship("Hints", backref="challenge")

    __mapper_args__ = {
        'polymorphic_identity': 'standard',
        'polymorphic_on': type
    }

    def __init__(self, name, description, value, category, type='standard'):
        self.name = name
        self.description = description
        self.value = value
        self.category = category
        self.type = type

    def __repr__(self):
        return '<Challenge %r>' % self.name


class Hints(db.Model):
    __tablename__ = 'hints'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    hint = db.Column(db.Text)
    cost = db.Column(db.Integer, default=0)
    requirements = db.Column(JSONLite)

    def __init__(self, challenge_id, hint, cost=0, type=0):
        self.challenge_id = challenge_id
        self.hint = hint
        self.cost = cost
        self.type = type

    def __repr__(self):
        return '<Hint %r>' % self.hint


class Awards(db.Model):
    __tablename__ = 'awards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    icon = db.Column(db.Text)
    requirements = db.Column(JSONLite)

    user = db.relationship('Users', foreign_keys="Awards.user_id", lazy='select')
    team = db.relationship('Teams', foreign_keys="Awards.team_id", lazy='select')

    def __init__(self, user_id, team_id, name, value):
        self.user_id = user_id
        self.team_id = team_id
        self.name = name
        self.value = value

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'value': self.value,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'date': self.date.isoformat()
        }
        return obj

    def __repr__(self):
        return '<Award %r>' % self.name


class Tags(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    chal_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    tag = db.Column(db.String(80))

    def __init__(self, chal, tag):
        self.chal = chal
        self.tag = tag

    def __repr__(self):
        return "<Tag {0} for challenge {1}>".format(self.tag, self.chal)


class Files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80))
    location = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return "<File type={type} location={location}>".format(type=self.type, location=self.location)


class ChallengeFiles(Files):
    __mapper_args__ = {
        'polymorphic_identity': 'challenges'
    }
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))

    def __init__(self, challenge_id, location):
        self.challenge_id = challenge_id
        self.location = location


class PageFiles(Files):
    __mapper_args__ = {
        'polymorphic_identity': 'pages'
    }
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))

    def __init__(self, page_id, location):
        self.page_id = page_id
        self.location = location


class Flags(db.Model):
    __tablename__ = 'flags'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    type = db.Column(db.String(80))
    flag = db.Column(db.Text)
    data = db.Column(db.Text)

    challenge = db.relationship('Challenges', foreign_keys="Flags.challenge_id", lazy='select')

    ## TODO: Perhaps this should also be Polymorphic so that plugins can subclass it.

    def __init__(self, challenge_id, flag, type):
        self.challenge_id = challenge_id
        self.flag = flag
        self.type = type

    def __repr__(self):
        return "<Flag {0} for challenge {1}>".format(self.flag, self.chal)


class Users(db.Model):
    __tablename__ = 'users'
    # Core attributes
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.Integer)
    name = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    admin = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(80))
    secret = db.Column(db.String(128))

    # Supplementary attributes
    website = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    country = db.Column(db.String(32))
    bracket = db.Column(db.String(32))
    hidden = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)

    # Relationship for Teams
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        self.password = hash_password(str(kwargs['password']))

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'name': self.name,
            'team_id': self.team_id,
            'website': self.website,
            'country': self.country,
            'bracket': self.bracket
        }
        return obj

    @property
    def score(self):
        return self.get_score(admin=False)

    def get_score(self, admin=False):
        score = db.func.sum(Challenges.value).label('score')
        user = db.session.query(
            Solves.user_id,
            Solves.challenge_id,
            score
        ) \
            .join(Users, Solves.user_id == Users.id) \
            .join(Challenges, Solves.challenge_id == Challenges.id) \
            .filter(Users.id == self.id)

        award_score = db.func.sum(Awards.value).label('award_score')
        award = db.session.query(award_score).filter_by(user_id=self.id)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                user = user.filter(Solves.date < freeze)
                award = award.filter(Awards.date < freeze)

        user = user.group_by(Solves.user_id).first()
        award = award.first()

        if user and award:
            return int(user.score or 0) + int(award.award_score or 0)
        elif user:
            return int(user.score or 0)
        elif award:
            return int(award.award_score or 0)
        else:
            return 0

    @property
    def place(self):
        return self.get_place(admin=False)

    def get_place(self, admin=False, numeric=False):
        """
        This method is generally a clone of CTFd.scoreboard.get_standings.
        The point being that models.py must be self-reliant and have little
        to no imports within the CTFd application as importing from the
        application itself will result in a circular import.
        """
        scores = db.session.query(
            Solves.user_id.label('user_id'),
            db.func.sum(Challenges.value).label('score'),
            db.func.max(Solves.id).label('id'),
            db.func.max(Solves.date).label('date')
        ).join(Challenges).filter(Challenges.value != 0).group_by(Solves.user_id)

        awards = db.session.query(
            Awards.user_id.label('user_id'),
            db.func.sum(Awards.value).label('score'),
            db.func.max(Awards.id).label('id'),
            db.func.max(Awards.date).label('date')
        ).filter(Awards.value != 0).group_by(Awards.user_id)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                scores = scores.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        results = union_all(scores, awards).alias('results')

        sumscores = db.session.query(
            results.columns.user_id,
            db.func.sum(results.columns.score).label('score'),
            db.func.max(results.columns.id).label('id'),
            db.func.max(results.columns.date).label('date')
        ).group_by(results.columns.user_id).subquery()

        if admin:
            standings_query = db.session.query(
                Users.id.label('user_id'),
            )\
                .join(sumscores, Users.id == sumscores.columns.user_id) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        else:
            standings_query = db.session.query(
                Users.id.label('user_id'),
            )\
                .join(sumscores, Users.id == sumscores.columns.user_id) \
                .filter(Users.banned == False) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)

        standings = standings_query.all()

        # http://codegolf.stackexchange.com/a/4712
        try:
            i = standings.index((self.id,)) + 1
            if numeric:
                return i
            else:
                k = i % 10
                return "%d%s" % (i, "tsnrhtdd"[(i / 10 % 10 != 1) * (k < 4) * k::4])
        except ValueError:
            return 0


class Admins(Users):
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }


class Teams(db.Model):
    __tablename__ = 'teams'
    # Core attributes
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.Integer)
    name = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    secret = db.Column(db.String(128))

    members = db.relationship("Users", backref="team")

    # Supplementary attributes
    website = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    country = db.Column(db.String(32))
    bracket = db.Column(db.String(32))
    hidden = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(Teams, self).__init__(**kwargs)
        self.password = hash_password(str(kwargs['password']))

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'country': self.country,
            'bracket': self.bracket,
            'members': [member.get_dict() for member in self.members]
        }
        return obj


    @property
    def score(self, admin=False):
        score = 0
        for member in self.members:
            score += member.score
        return score

    @property
    def place(self, admin=False):
        """
        This method is generally a clone of CTFd.scoreboard.get_standings.
        The point being that models.py must be self-reliant and have little
        to no imports within the CTFd application as importing from the
        application itself will result in a circular import.
        """
        scores = db.session.query(
            Solves.team_id.label('team_id'),
            db.func.sum(Challenges.value).label('score'),
            db.func.max(Solves.id).label('id'),
            db.func.max(Solves.date).label('date')
        ).join(Challenges).filter(Challenges.value != 0).group_by(Solves.team_id)

        awards = db.session.query(
            Awards.team_id.label('team_id'),
            db.func.sum(Awards.value).label('score'),
            db.func.max(Awards.id).label('id'),
            db.func.max(Awards.date).label('date')
        ).filter(Awards.value != 0).group_by(Awards.team_id)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                scores = scores.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        results = union_all(scores, awards).alias('results')

        sumscores = db.session.query(
            results.columns.team_id,
            db.func.sum(results.columns.score).label('score'),
            db.func.max(results.columns.id).label('id'),
            db.func.max(results.columns.date).label('date')
        ).group_by(results.columns.team_id).subquery()

        if admin:
            standings_query = db.session.query(
                Teams.id.label('team_id'),
            )\
                .join(sumscores, Teams.id == sumscores.columns.team_id) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        else:
            standings_query = db.session.query(
                Teams.id.label('team_id'),
            )\
                .join(sumscores, Teams.id == sumscores.columns.team_id) \
                .filter(Teams.banned == False) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)

        standings = standings_query.all()

        # http://codegolf.stackexchange.com/a/4712
        try:
            i = standings.index((self.id,)) + 1
            k = i % 10
            return "%d%s" % (i, "tsnrhtdd"[(i / 10 % 10 != 1) * (k < 4) * k::4])
        except ValueError:
            return 0


class Submissions(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    ip = db.Column(db.String(46))
    provided = db.Column(db.Text)
    type = db.Column(db.String(32))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = db.relationship('Users', foreign_keys="Submissions.user_id", lazy='select')
    team = db.relationship('Teams', foreign_keys="Submissions.team_id", lazy='select')
    challenge = db.relationship('Challenges', foreign_keys="Submissions.challenge_id", lazy='select')

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'date': self.date.isoformat()
        }
        return obj

    def __repr__(self):
        return '<Submission {}, {}, {}, {}>'.format(self.team_id, self.chal_id, self.ip, self.provided)


class Solves(Submissions):
    __tablename__ = 'solves'
    __table_args__ = (db.UniqueConstraint('challenge_id', 'user_id'), {})
    id = db.Column(None, db.ForeignKey('submissions.id'), primary_key=True)
    challenge_id = column_property(db.Column(db.Integer, db.ForeignKey('challenges.id')), Submissions.challenge_id)
    user_id = column_property(db.Column(db.Integer, db.ForeignKey('users.id')), Submissions.user_id)

    user = db.relationship('Users', foreign_keys="Solves.user_id", lazy='select')
    challenge = db.relationship('Challenges', foreign_keys="Solves.challenge_id", lazy='select')

    __mapper_args__ = {
        'polymorphic_identity': 'correct'
    }


class Fails(Submissions):
    __mapper_args__ = {
        'polymorphic_identity': 'incorrect'
    }


class Unlocks(db.Model):
    __tablename__ = 'unlocks'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    item_id = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    type = db.Column(db.String(32))

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __init__(self, type, team_id, item_id):
        self.type = type
        self.team_id = team_id
        self.item_id = item_id

    def __repr__(self):
        return '<Unlock %r>' % self.teamid


class ChallengesUnlocks(Unlocks):
    __mapper_args__ = {
        'polymorphic_identity': 'challenges'
    }


class AwardUnlocks(Unlocks):
    __mapper_args__ = {
        'polymorphic_identity': 'awards'
    }


class HintUnlocks(Unlocks):
    __mapper_args__ = {
        'polymorphic_identity': 'hints'
    }


class Tracking(db.Model):
    # TODO: Perhaps add polymorphic here and create types of Tracking so that we can have an audit log
    __tablename__ = 'tracking'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(46))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('Users', foreign_keys="Tracking.user_id", lazy='select')

    def __init__(self, ip, user_id):
        self.ip = ip
        self.user_id = user_id

    def __repr__(self):
        return '<Tracking %r>' % self.team


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value
