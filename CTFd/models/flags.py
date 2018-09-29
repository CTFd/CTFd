from CTFd.models import db


class Flags(db.Model):
    __tablename__ = 'flags'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    type = db.Column(db.String(80))
    content = db.Column(db.Text)
    data = db.Column(db.Text)

    challenge = db.relationship('Challenges', foreign_keys="Flags.challenge_id", lazy='select')

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, *args, **kwargs):
        super(Flags, self).__init__(**kwargs)

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'type': self.type,
            'content': self.flag,
            'data': self.data,
        }
        return obj

    def __repr__(self):
        return "<Flag {0} for challenge {1}>".format(self.flag, self.chal)