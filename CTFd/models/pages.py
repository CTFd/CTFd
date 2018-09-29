from CTFd.models import db


class Pages(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    auth_required = db.Column(db.Boolean)
    title = db.Column(db.String(80))
    route = db.Column(db.Text, unique=True)
    html = db.Column(db.Text)
    draft = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    # TODO: Use hidden attribute

    files = db.relationship("PageFiles", backref="page")

    def __init__(self, *args, **kwargs):
        super(Pages, self).__init__(**kwargs)

    # def __init__(self, title, route, html, draft=True, auth_required=False):
    #     self.title = title
    #     self.route = route
    #     self.html = html
    #     self.draft = draft
    #     self.auth_required = auth_required

    def __repr__(self):
        return "<Pages {0}>".format(self.route)