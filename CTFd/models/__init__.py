import datetime
from collections import defaultdict

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, validates

from CTFd.cache import cache

db = SQLAlchemy()
ma = Marshmallow()


def get_class_by_tablename(tablename):
    """Return class reference mapped to table.
    https://stackoverflow.com/a/23754464

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    for c in db.Model._decl_class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == tablename:
            return c
    return None


class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))

    user = db.relationship("Users", foreign_keys="Notifications.user_id", lazy="select")
    team = db.relationship("Teams", foreign_keys="Notifications.team_id", lazy="select")

    def __init__(self, *args, **kwargs):
        super(Notifications, self).__init__(**kwargs)


class Pages(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    route = db.Column(db.String(128), unique=True)
    content = db.Column(db.Text)
    draft = db.Column(db.Boolean)
    hidden = db.Column(db.Boolean)
    auth_required = db.Column(db.Boolean)
    # TODO: Use hidden attribute

    files = db.relationship("PageFiles", backref="page")

    def __init__(self, *args, **kwargs):
        super(Pages, self).__init__(**kwargs)

    def __repr__(self):
        return "<Pages {0}>".format(self.route)


class Challenges(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=0)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    type = db.Column(db.String(80))
    state = db.Column(db.String(80), nullable=False, default="visible")
    requirements = db.Column(db.JSON)

    files = db.relationship("ChallengeFiles", backref="challenge")
    tags = db.relationship("Tags", backref="challenge")
    hints = db.relationship("Hints", backref="challenge")
    flags = db.relationship("Flags", backref="challenge")

    class alt_defaultdict(defaultdict):
        """
        This slightly modified defaultdict is intended to allow SQLAlchemy to
        not fail when querying Challenges that contain a missing challenge type.

        e.g. Challenges.query.all() should not fail if `type` is `a_missing_type`
        """

        def __missing__(self, key):
            return self["standard"]

    __mapper_args__ = {
        "polymorphic_identity": "standard",
        "polymorphic_on": type,
        "_polymorphic_map": alt_defaultdict(),
    }

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.description))

    def __init__(self, *args, **kwargs):
        super(Challenges, self).__init__(**kwargs)

    def __repr__(self):
        return "<Challenge %r>" % self.name


class Hints(db.Model):
    __tablename__ = "hints"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    content = db.Column(db.Text)
    cost = db.Column(db.Integer, default=0)
    requirements = db.Column(db.JSON)

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    @property
    def name(self):
        return "Hint {id}".format(id=self.id)

    @property
    def category(self):
        return self.__tablename__

    @property
    def description(self):
        return "Hint for {name}".format(name=self.challenge.name)

    @property
    def html(self):
        from CTFd.utils.config.pages import build_html
        from CTFd.utils.helpers import markup

        return markup(build_html(self.content))

    def __init__(self, *args, **kwargs):
        super(Hints, self).__init__(**kwargs)

    def __repr__(self):
        return "<Hint %r>" % self.content


class Awards(db.Model):
    __tablename__ = "awards"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    type = db.Column(db.String(80), default="standard")
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    icon = db.Column(db.Text)
    requirements = db.Column(db.JSON)

    user = db.relationship("Users", foreign_keys="Awards.user_id", lazy="select")
    team = db.relationship("Teams", foreign_keys="Awards.team_id", lazy="select")

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.user_id

    def __init__(self, *args, **kwargs):
        super(Awards, self).__init__(**kwargs)

    def __repr__(self):
        return "<Award %r>" % self.name


class Tags(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    value = db.Column(db.String(80))

    def __init__(self, *args, **kwargs):
        super(Tags, self).__init__(**kwargs)


class Files(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), default="standard")
    location = db.Column(db.Text)

    __mapper_args__ = {"polymorphic_identity": "standard", "polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Files, self).__init__(**kwargs)

    def __repr__(self):
        return "<File type={type} location={location}>".format(
            type=self.type, location=self.location
        )


class ChallengeFiles(Files):
    __mapper_args__ = {"polymorphic_identity": "challenge"}
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )

    def __init__(self, *args, **kwargs):
        super(ChallengeFiles, self).__init__(**kwargs)


class PageFiles(Files):
    __mapper_args__ = {"polymorphic_identity": "page"}
    page_id = db.Column(db.Integer, db.ForeignKey("pages.id"))

    def __init__(self, *args, **kwargs):
        super(PageFiles, self).__init__(**kwargs)


class Flags(db.Model):
    __tablename__ = "flags"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    type = db.Column(db.String(80))
    content = db.Column(db.Text)
    data = db.Column(db.Text)

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Flags, self).__init__(**kwargs)

    def __repr__(self):
        return "<Flag {0} for challenge {1}>".format(self.content, self.challenge_id)


class Users(db.Model):
    __tablename__ = "users"
    __table_args__ = (db.UniqueConstraint("id", "oauth_id"), {})
    # Core attributes
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.Integer, unique=True)
    # User names are not constrained to be unique to allow for official/unofficial teams.
    name = db.Column(db.String(128))
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    type = db.Column(db.String(80))
    secret = db.Column(db.String(128))

    # Supplementary attributes
    website = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    country = db.Column(db.String(32))
    bracket = db.Column(db.String(32))
    hidden = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)

    # Relationship for Teams
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": type}

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)

    @validates("password")
    def validate_password(self, key, plaintext):
        from CTFd.utils.crypto import hash_password

        return hash_password(str(plaintext))

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.id

    @hybrid_property
    def account(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team
        elif user_mode == "users":
            return self

    @property
    def solves(self):
        return self.get_solves(admin=False)

    @property
    def fails(self):
        return self.get_fails(admin=False)

    @property
    def awards(self):
        return self.get_awards(admin=False)

    @property
    def score(self):
        return self.get_score(admin=False)

    @property
    def place(self):
        from CTFd.utils.config.visibility import scores_visible

        if scores_visible():
            return self.get_place(admin=False)
        else:
            return None

    def get_solves(self, admin=False):
        from CTFd.utils import get_config

        solves = Solves.query.filter_by(user_id=self.id)
        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            solves = solves.filter(Solves.date < dt)
        return solves.all()

    def get_fails(self, admin=False):
        from CTFd.utils import get_config

        fails = Fails.query.filter_by(user_id=self.id)
        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            fails = fails.filter(Fails.date < dt)
        return fails.all()

    def get_awards(self, admin=False):
        from CTFd.utils import get_config

        awards = Awards.query.filter_by(user_id=self.id)
        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            awards = awards.filter(Awards.date < dt)
        return awards.all()

    @cache.memoize()
    def get_score(self, admin=False):
        score = db.func.sum(Challenges.value).label("score")
        user = (
            db.session.query(Solves.user_id, score)
            .join(Users, Solves.user_id == Users.id)
            .join(Challenges, Solves.challenge_id == Challenges.id)
            .filter(Users.id == self.id)
        )

        award_score = db.func.sum(Awards.value).label("award_score")
        award = db.session.query(award_score).filter_by(user_id=self.id)

        if not admin:
            freeze = Configs.query.filter_by(key="freeze").first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                user = user.filter(Solves.date < freeze)
                award = award.filter(Awards.date < freeze)

        user = user.group_by(Solves.user_id).first()
        award = award.first()

        if user and award:
            return int(user.score or 0) + int(award.award_score or 0)
        elif user:
            return int(user.score or 0)
        elif award:
            return int(award.award_score or 0)
        else:
            return 0

    @cache.memoize()
    def get_place(self, admin=False, numeric=False):
        """
        This method is generally a clone of CTFd.scoreboard.get_standings.
        The point being that models.py must be self-reliant and have little
        to no imports within the CTFd application as importing from the
        application itself will result in a circular import.
        """
        from CTFd.utils.scores import get_user_standings
        from CTFd.utils.humanize.numbers import ordinalize

        standings = get_user_standings(admin=admin)

        for i, user in enumerate(standings):
            if user.user_id == self.id:
                n = i + 1
                if numeric:
                    return n
                return ordinalize(n)
        else:
            return None


class Admins(Users):
    __tablename__ = "admins"
    __mapper_args__ = {"polymorphic_identity": "admin"}


class Teams(db.Model):
    __tablename__ = "teams"
    __table_args__ = (db.UniqueConstraint("id", "oauth_id"), {})
    # Core attributes
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.Integer, unique=True)
    # Team names are not constrained to be unique to allow for official/unofficial teams.
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    secret = db.Column(db.String(128))

    members = db.relationship(
        "Users", backref="team", foreign_keys="Users.team_id", lazy="joined"
    )

    # Supplementary attributes
    website = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    country = db.Column(db.String(32))
    bracket = db.Column(db.String(32))
    hidden = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)

    # Relationship for Users
    captain_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    captain = db.relationship("Users", foreign_keys=[captain_id])

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(Teams, self).__init__(**kwargs)

    @validates("password")
    def validate_password(self, key, plaintext):
        from CTFd.utils.crypto import hash_password

        return hash_password(str(plaintext))

    @property
    def solves(self):
        return self.get_solves(admin=False)

    @property
    def fails(self):
        return self.get_fails(admin=False)

    @property
    def awards(self):
        return self.get_awards(admin=False)

    @property
    def score(self):
        return self.get_score(admin=False)

    @property
    def place(self):
        from CTFd.utils.config.visibility import scores_visible

        if scores_visible():
            return self.get_place(admin=False)
        else:
            return None

    def get_solves(self, admin=False):
        from CTFd.utils import get_config

        member_ids = [member.id for member in self.members]

        solves = Solves.query.filter(Solves.user_id.in_(member_ids)).order_by(
            Solves.date.asc()
        )

        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            solves = solves.filter(Solves.date < dt)

        return solves.all()

    def get_fails(self, admin=False):
        from CTFd.utils import get_config

        member_ids = [member.id for member in self.members]

        fails = Fails.query.filter(Fails.user_id.in_(member_ids)).order_by(
            Fails.date.asc()
        )

        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            fails = fails.filter(Fails.date < dt)

        return fails.all()

    def get_awards(self, admin=False):
        from CTFd.utils import get_config

        member_ids = [member.id for member in self.members]

        awards = Awards.query.filter(Awards.user_id.in_(member_ids)).order_by(
            Awards.date.asc()
        )

        freeze = get_config("freeze")
        if freeze and admin is False:
            dt = datetime.datetime.utcfromtimestamp(freeze)
            awards = awards.filter(Awards.date < dt)

        return awards.all()

    @cache.memoize()
    def get_score(self, admin=False):
        score = 0
        for member in self.members:
            score += member.get_score(admin=admin)
        return score

    @cache.memoize()
    def get_place(self, admin=False, numeric=False):
        """
        This method is generally a clone of CTFd.scoreboard.get_standings.
        The point being that models.py must be self-reliant and have little
        to no imports within the CTFd application as importing from the
        application itself will result in a circular import.
        """
        from CTFd.utils.scores import get_team_standings
        from CTFd.utils.humanize.numbers import ordinalize

        standings = get_team_standings(admin=admin)

        for i, team in enumerate(standings):
            if team.team_id == self.id:
                n = i + 1
                if numeric:
                    return n
                return ordinalize(n)
        else:
            return None


class Submissions(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    ip = db.Column(db.String(46))
    provided = db.Column(db.Text)
    type = db.Column(db.String(32))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = db.relationship("Users", foreign_keys="Submissions.user_id", lazy="select")
    team = db.relationship("Teams", foreign_keys="Submissions.team_id", lazy="select")
    challenge = db.relationship(
        "Challenges", foreign_keys="Submissions.challenge_id", lazy="select"
    )

    __mapper_args__ = {"polymorphic_on": type}

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.user_id

    @hybrid_property
    def account(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team
        elif user_mode == "users":
            return self.user

    @staticmethod
    def get_child(type):
        child_classes = {
            x.polymorphic_identity: x.class_
            for x in Submissions.__mapper__.self_and_descendants
        }
        return child_classes[type]

    def __repr__(self):
        return "<Submission {}, {}, {}, {}>".format(
            self.team_id, self.challenge_id, self.ip, self.provided
        )


class Solves(Submissions):
    __tablename__ = "solves"
    __table_args__ = (
        db.UniqueConstraint("challenge_id", "user_id"),
        db.UniqueConstraint("challenge_id", "team_id"),
        {},
    )
    id = db.Column(
        None, db.ForeignKey("submissions.id", ondelete="CASCADE"), primary_key=True
    )
    challenge_id = column_property(
        db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE")),
        Submissions.challenge_id,
    )
    user_id = column_property(
        db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE")),
        Submissions.user_id,
    )
    team_id = column_property(
        db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE")),
        Submissions.team_id,
    )

    user = db.relationship("Users", foreign_keys="Solves.user_id", lazy="select")
    team = db.relationship("Teams", foreign_keys="Solves.team_id", lazy="select")
    challenge = db.relationship(
        "Challenges", foreign_keys="Solves.challenge_id", lazy="select"
    )

    __mapper_args__ = {"polymorphic_identity": "correct"}


class Fails(Submissions):
    __mapper_args__ = {"polymorphic_identity": "incorrect"}


class Unlocks(db.Model):
    __tablename__ = "unlocks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"))
    target = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    type = db.Column(db.String(32))

    __mapper_args__ = {"polymorphic_on": type}

    @hybrid_property
    def account_id(self):
        from CTFd.utils import get_config

        user_mode = get_config("user_mode")
        if user_mode == "teams":
            return self.team_id
        elif user_mode == "users":
            return self.user_id

    def __repr__(self):
        return "<Unlock %r>" % self.id


class HintUnlocks(Unlocks):
    __mapper_args__ = {"polymorphic_identity": "hints"}


class Tracking(db.Model):
    __tablename__ = "tracking"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    ip = db.Column(db.String(46))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("Users", foreign_keys="Tracking.user_id", lazy="select")

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Tracking, self).__init__(**kwargs)

    def __repr__(self):
        return "<Tracking %r>" % self.ip


class Configs(db.Model):
    __tablename__ = "config"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(Configs, self).__init__(**kwargs)


class Tokens(db.Model):
    __tablename__ = "tokens"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expiration = db.Column(
        db.DateTime,
        default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=30),
    )
    value = db.Column(db.String(128), unique=True)

    user = db.relationship("Users", foreign_keys="Tokens.user_id", lazy="select")

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super(Tokens, self).__init__(**kwargs)

    def __repr__(self):
        return "<Token %r>" % self.id


class UserTokens(Tokens):
    __mapper_args__ = {"polymorphic_identity": "user"}
