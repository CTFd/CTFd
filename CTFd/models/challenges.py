from CTFd.models import db, JSONLite


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

    def __init__(self, *args, **kwargs):
        super(Challenges, self).__init__(**kwargs)

    # def __init__(self, name, description, value, category, type='standard'):
    #     self.name = name
    #     self.description = description
    #     self.value = value
    #     self.category = category
    #     self.type = type

    def __repr__(self):
        return '<Challenge %r>' % self.name