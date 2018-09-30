from CTFd.models import db
import datetime


class Tracking(db.Model):
    # TODO: Perhaps add polymorphic here and create types of Tracking so that we can have an audit log
    __tablename__ = 'tracking'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    ip = db.Column(db.String(46))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('Users', foreign_keys="Tracking.user_id", lazy='select')

    # def __init__(self, ip, user_id):
    #     self.ip = ip
    #     self.user_id = user_id

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __init__(self, *args, **kwargs):
        super(Tracking, self).__init__(**kwargs)