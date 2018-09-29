from sqlalchemy.orm import validates, column_property
from CTFd.models import db
import datetime


class Submissions(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='CASCADE'))
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
            'type': self.type,
            'challenge_id': self.challenge_id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'provided': self.provided,
            'date': self.date.isoformat(),
        }
        return obj

    def __repr__(self):
        return '<Submission {}, {}, {}, {}>'.format(self.team_id, self.chal_id, self.ip, self.provided)


class Solves(Submissions):
    __tablename__ = 'solves'
    __table_args__ = (db.UniqueConstraint('challenge_id', 'user_id'), {})
    id = db.Column(
        None,
        db.ForeignKey('submissions.id', ondelete='CASCADE'),
        primary_key=True
    )
    challenge_id = column_property(
        db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE')),
        Submissions.challenge_id
    )
    user_id = column_property(
        db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
        Submissions.user_id
    )

    user = db.relationship('Users', foreign_keys="Solves.user_id", lazy='select')
    challenge = db.relationship('Challenges', foreign_keys="Solves.challenge_id", lazy='select')

    __mapper_args__ = {
        'polymorphic_identity': 'correct'
    }


class Fails(Submissions):
    __mapper_args__ = {
        'polymorphic_identity': 'incorrect'
    }