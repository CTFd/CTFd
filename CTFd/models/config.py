from CTFd.models import db


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(**kwargs)