from CTFd.models import db

# Weak Entity On Users
class CSAWMembers(db.Model):
    __tablename__ = "csaw_members"

    # fields
    sub_id = db.Column(db.Integer, primary_key=True)  # 0,1,2,3
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    school = db.Column(db.String(128))
