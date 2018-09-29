from CTFd.models import db


class Files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80))
    location = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return "<File type={type} location={location}>".format(type=self.type, location=self.location)


class ChallengeFiles(Files):
    __mapper_args__ = {
        'polymorphic_identity': 'challenges'
    }
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))

    def __init__(self, challenge_id, location):
        self.challenge_id = challenge_id
        self.location = location


class PageFiles(Files):
    __mapper_args__ = {
        'polymorphic_identity': 'pages'
    }
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))

    def __init__(self, page_id, location):
        self.page_id = page_id
        self.location = location