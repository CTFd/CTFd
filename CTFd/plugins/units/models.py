import datetime

from CTFd.models import db


class Units(db.Model):
    __tablename__ = "units"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    emblem_path = db.Column(db.String(512), default="")
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    members = db.relationship(
        "UserUnits", backref="unit", lazy="select", cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        super(Units, self).__init__(**kwargs)

    def __repr__(self):
        return "<Unit %r>" % self.name


class UserUnits(db.Model):
    __tablename__ = "user_units"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    unit_id = db.Column(
        db.Integer,
        db.ForeignKey("units.id", ondelete="CASCADE"),
        nullable=False,
    )

    def __init__(self, *args, **kwargs):
        super(UserUnits, self).__init__(**kwargs)

    def __repr__(self):
        return "<UserUnit user_id=%r unit_id=%r>" % (self.user_id, self.unit_id)
