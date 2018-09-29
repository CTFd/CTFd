from CTFd.models import db, JSONLite
import datetime

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

    def __init__(self, *args, **kwargs):
        super(Awards, self).__init__(**kwargs)

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