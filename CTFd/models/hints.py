from CTFd.models import db, JSONLite


class Hints(db.Model):
    __tablename__ = 'hints'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    hint = db.Column(db.Text)
    cost = db.Column(db.Integer, default=0)
    requirements = db.Column(JSONLite)

    # def __init__(self, challenge_id, hint, cost=0, type=0):
    #     self.challenge_id = challenge_id
    #     self.hint = hint
    #     self.cost = cost
    #     self.type = type

    def __init__(self, *args, **kwargs):
        super(Hints, self).__init__(**kwargs)

    def get_dict(self, admin=False):
        obj = {
            'id': self.id,
            'type': self.type,
            'challenge_id': self.challenge_id,
            'hint': self.hint,
            'cost': self.cost,
        }
        return obj

    def __repr__(self):
        return '<Hint %r>' % self.hint