from sqlalchemy.sql.expression import union_all
from CTFd.models import db
from CTFd.models.challenges import Challenges
from CTFd.models.submissions import Solves
from CTFd.models.awards import Awards
from CTFd.models.config import Config
from CTFd.utils.crypto import hash_password
import datetime


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
            ) \
                .join(sumscores, Users.id == sumscores.columns.user_id) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        else:
            standings_query = db.session.query(
                Users.id.label('user_id'),
            ) \
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