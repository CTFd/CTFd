from CTFd.models import db
import datetime


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