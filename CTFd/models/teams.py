from sqlalchemy.sql.expression import union_all
from CTFd.models import db
from CTFd.models.challenges import Challenges
from CTFd.models.submissions import Solves
from CTFd.models.awards import Awards
from CTFd.models.config import Config
from CTFd.utils.crypto import hash_password
import datetime


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
            ) \
                .join(sumscores, Teams.id == sumscores.columns.team_id) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        else:
            standings_query = db.session.query(
                Teams.id.label('team_id'),
            ) \
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