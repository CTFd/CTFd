from CTFd.models import db


class Tags(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    value = db.Column(db.String(80))

    def __init__(self, challenge_id, value):
        self.challenge_id = challenge_id
        self.value = value

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'challenge_id': self.challenge_id,
            'value': self.tag,
        }
        return obj

    def __repr__(self):
        return "<Tag {0} for challenge {1}>".format(self.tag, self.chal)