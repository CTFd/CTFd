import datetime
import hashlib
import json
import netaddr
from socket import inet_pton, inet_ntop, AF_INET, AF_INET6
from struct import unpack, pack, error as struct_error

from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt_sha256
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql.expression import union_all


def sha512(string):
    return str(hashlib.sha512(string).hexdigest())


def ip2long(ip):
    '''Converts a user's IP address into an integer/long'''
    return int(netaddr.IPAddress(ip))


def long2ip(ip_int):
    '''Converts a saved integer/long back into an IP address'''
    return str(netaddr.IPAddress(ip_int))


db = SQLAlchemy()


class Pages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(80), unique=True)
    html = db.Column(db.Text)

    def __init__(self, route, html):
        self.route = route
        self.html = html

    def __repr__(self):
        return "<Pages route {0}>".format(self.route)


class Challenges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=0)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    type = db.Column(db.Integer)
    hidden = db.Column(db.Boolean)

    def __init__(self, name, description, value, category, type=0):
        self.name = name
        self.description = description
        self.value = value
        self.category = category
        self.type = type
        # self.flags = json.dumps(flags)

    def __repr__(self):
        return '<chal %r>' % self.name


class Hints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    hint = db.Column(db.Text)
    cost = db.Column(db.Integer, default=0)

    def __init__(self, chal, hint, cost=0, type=0):
        self.chal = chal
        self.hint = hint
        self.cost = cost
        self.type = type

    def __repr__(self):
        return '<hint %r>' % self.hint


class Awards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    icon = db.Column(db.Text)

    def __init__(self, teamid, name, value):
        self.teamid = teamid
        self.name = name
        self.value = value

    def __repr__(self):
        return '<award %r>' % self.name


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    tag = db.Column(db.String(80))

    def __init__(self, chal, tag):
        self.chal = chal
        self.tag = tag

    def __repr__(self):
        return "<Tag {0} for challenge {1}>".format(self.tag, self.chal)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    location = db.Column(db.Text)

    def __init__(self, chal, location):
        self.chal = chal
        self.location = location

    def __repr__(self):
        return "<File {0} for challenge {1}>".format(self.location, self.chal)


class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chal = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    key_type = db.Column(db.Integer)
    flag = db.Column(db.Text)
    data = db.Column(db.Text)

    def __init__(self, chal, flag, key_type):
        self.chal = chal
        self.flag = flag
        self.key_type = key_type

    def __repr__(self):
        return "<Flag {0} for challenge {1}>".format(self.flag, self.chal)


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    website = db.Column(db.String(128))
    affiliation = db.Column(db.String(128))
    country = db.Column(db.String(32))
    bracket = db.Column(db.String(32))
    banned = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt_sha256.encrypt(str(password))

    def __repr__(self):
        return '<team %r>' % self.name

    def score(self, admin=False):
        score = db.func.sum(Challenges.value).label('score')
        team = db.session.query(Solves.teamid, score).join(Teams).join(Challenges).filter(Teams.id == self.id)
        award_score = db.func.sum(Awards.value).label('award_score')
        award = db.session.query(award_score).filter_by(teamid=self.id)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                team = team.filter(Solves.date < freeze)
                award = award.filter(Awards.date < freeze)

        team = team.group_by(Solves.teamid).first()
        award = award.first()

        if team and award:
            return int(team.score or 0) + int(award.award_score or 0)
        elif team:
            return int(team.score or 0)
        elif award:
            return int(award.award_score or 0)
        else:
            return 0

    def place(self, admin=False):
        scores = db.session.query(
            Solves.teamid.label('teamid'),
            db.func.sum(Challenges.value).label('score'),
            db.func.max(Solves.date).label('date')
        ).join(Challenges).group_by(Solves.teamid)

        awards = db.session.query(
            Awards.teamid.label('teamid'),
            db.func.sum(Awards.value).label('score'),
            db.func.max(Awards.date).label('date')
        ).group_by(Awards.teamid)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                scores = scores.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        results = union_all(scores, awards).alias('results')

        sumscore = db.func.sum(results.columns.score).label('sumscore')
        quickest = db.func.max(results.columns.date).label('quickest')

        standings_query = db.session.query(results.columns.teamid)\
            .join(Teams)\
            .group_by(results.columns.teamid)\
            .order_by(sumscore.desc(), quickest)

        if not admin:
            standings_query = standings_query.filter(Teams.banned == False)

        standings = standings_query.all()

        # http://codegolf.stackexchange.com/a/4712
        try:
            i = standings.index((self.id,)) + 1
            k = i % 10
            return "%d%s" % (i, "tsnrhtdd"[(i / 10 % 10 != 1) * (k < 4) * k::4])
        except ValueError:
            return 0


class Solves(db.Model):
    __table_args__ = (db.UniqueConstraint('chalid', 'teamid'), {})
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    ip = db.Column(db.String(46))
    flag = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    team = db.relationship('Teams', foreign_keys="Solves.teamid", lazy='joined')
    chal = db.relationship('Challenges', foreign_keys="Solves.chalid", lazy='joined')
    # value = db.Column(db.Integer)

    def __init__(self, teamid, chalid, ip, flag):
        self.ip = ip
        self.chalid = chalid
        self.teamid = teamid
        self.flag = flag
        # self.value = value

    def __repr__(self):
        return '<solve {}, {}, {}, {}>'.format(self.teamid, self.chalid, self.ip, self.flag)


class WrongKeys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chalid = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    ip = db.Column(db.String(46))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    flag = db.Column(db.Text)
    chal = db.relationship('Challenges', foreign_keys="WrongKeys.chalid", lazy='joined')

    def __init__(self, teamid, chalid, ip, flag):
        self.ip = ip
        self.teamid = teamid
        self.chalid = chalid
        self.flag = flag

    def __repr__(self):
        return '<wrong {}, {}, {}, {}>'.format(self.teamid, self.chalid, self.ip, self.flag)


class Unlocks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    itemid = db.Column(db.Integer)
    model = db.Column(db.String(32))

    def __init__(self, model, teamid, itemid):
        self.model = model
        self.teamid = teamid
        self.itemid = itemid

    def __repr__(self):
        return '<unlock %r>' % self.teamid


class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(46))
    team = db.Column(db.Integer, db.ForeignKey('teams.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, ip, team):
        self.ip = ip
        self.team = team

    def __repr__(self):
        return '<ip %r>' % self.team


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value
