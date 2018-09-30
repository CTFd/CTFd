from CTFd.models import db
import datetime


class Announcements(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(Announcements, self).__init__(**kwargs)

    # def __init__(self, content):
    #     self.content = content