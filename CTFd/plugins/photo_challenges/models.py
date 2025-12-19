from CTFd.models import db
from sqlalchemy.sql import func


class PhotoSubmission(db.Model):
    __tablename__ = "photo_submissions"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, nullable=False)
    challenge_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(256))
    filepath = db.Column(db.String(512))
    status = db.Column(db.String(32), default="pending") # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, server_default=func.now())
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
