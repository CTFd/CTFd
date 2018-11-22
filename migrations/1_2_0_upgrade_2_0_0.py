import sys
import os

# This is important to allow access to the CTFd application factory
sys.path.append(os.getcwd())

import datetime
import hashlib
import netaddr
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql.expression import union_all
from CTFd import config, create_app
from sqlalchemy_utils import (
    drop_database,
)
from six.moves import input

import dataset


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
    auth_required = db.Column(db.Boolean)
    title = db.Column(db.String(80))
    route = db.Column(db.Text, unique=True)
    html = db.Column(db.Text)
    draft = db.Column(db.Boolean)

    def __init__(self, title, route, html, draft=True, auth_required=False):
        self.title = title
        self.route = route
        self.html = html
        self.draft = draft
        self.auth_required = auth_required

    def __repr__(self):
        return "<Pages route {0}>".format(self.route)


class Challenges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=0)
    value = db.Column(db.Integer)
    category = db.Column(db.String(80))
    type = db.Column(db.String(80))
    hidden = db.Column(db.Boolean)
    __mapper_args__ = {
        'polymorphic_identity': 'standard',
        'polymorphic_on': type
    }

    def __init__(self, name, description, value, category, type='standard'):
        self.name = name
        self.description = description
        self.value = value
        self.category = category
        self.type = type

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
    type = db.Column(db.String(80))
    flag = db.Column(db.Text)
    data = db.Column(db.Text)

    def __init__(self, chal, flag, type):
        self.chal = chal
        self.flag = flag
        self.type = type

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
        """
        This method is generally a clone of CTFd.scoreboard.get_standings.
        The point being that models.py must be self-reliant and have little
        to no imports within the CTFd application as importing from the
        application itself will result in a circular import.
        """
        scores = db.session.query(
            Solves.teamid.label('teamid'),
            db.func.sum(Challenges.value).label('score'),
            db.func.max(Solves.id).label('id'),
            db.func.max(Solves.date).label('date')
        ).join(Challenges).filter(Challenges.value != 0).group_by(Solves.teamid)

        awards = db.session.query(
            Awards.teamid.label('teamid'),
            db.func.sum(Awards.value).label('score'),
            db.func.max(Awards.id).label('id'),
            db.func.max(Awards.date).label('date')
        ).filter(Awards.value != 0).group_by(Awards.teamid)

        if not admin:
            freeze = Config.query.filter_by(key='freeze').first()
            if freeze and freeze.value:
                freeze = int(freeze.value)
                freeze = datetime.datetime.utcfromtimestamp(freeze)
                scores = scores.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        results = union_all(scores, awards).alias('results')

        sumscores = db.session.query(
            results.columns.teamid,
            db.func.sum(results.columns.score).label('score'),
            db.func.max(results.columns.id).label('id'),
            db.func.max(results.columns.date).label('date')
        ).group_by(results.columns.teamid).subquery()

        if admin:
            standings_query = db.session.query(
                Teams.id.label('teamid'),
            ) \
                .join(sumscores, Teams.id == sumscores.columns.teamid) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
        else:
            standings_query = db.session.query(
                Teams.id.label('teamid'),
            ) \
                .join(sumscores, Teams.id == sumscores.columns.teamid) \
                .filter(Teams.banned == False) \
                .order_by(sumscores.columns.score.desc(), sumscores.columns.id)

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


if __name__ == '__main__':
    print("/*\\ Migrating your database to 2.0.0 can potentially lose data./*\\")
    print("""/*\\ Please be sure to back up all data by:
        * creating a CTFd export
        * creating a dump of your actual database
        * and backing up the CTFd source code directory""")
    print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
    if input('Run database migrations (Y/N)').lower().strip() == 'y':
        pass
    else:
        print('/*\\ Aborting database migrations... /*\\')
        print('/*\\ Exiting... /*\\')
        exit(1)

    db_url = config.Config.SQLALCHEMY_DATABASE_URI
    old_data = {}

    old_conn = dataset.connect(config.Config.SQLALCHEMY_DATABASE_URI)
    tables = old_conn.tables
    for table in tables:
        old_data[table] = old_conn[table].all()

    if 'alembic_version' in old_data:
        old_data.pop('alembic_version')

    print('Current Tables:')
    for table in old_data.keys():
        print(table)

    old_conn.executable.close()

    print('DROPPING DATABASE')
    drop_database(db_url)

    app = create_app()

    new_conn = dataset.connect(config.Config.SQLALCHEMY_DATABASE_URI)

    print('MIGRATING Challenges')
    for challenge in old_data['challenges']:
        hidden = challenge.pop('hidden')
        challenge['state'] = 'hidden' if hidden else 'visible'
        new_conn['challenges'].insert(dict(challenge))
    del old_data['challenges']

    print('MIGRATING Teams')
    for team in old_data['teams']:
        admin = team.pop('admin')
        team['type'] = 'admin' if admin else 'user'
        team['hidden'] = bool(team.pop('banned'))
        team['banned'] = False
        team['verified'] = bool(team.pop('verified'))
        new_conn['users'].insert(dict(team))
    del old_data['teams']

    print('MIGRATING Pages')
    for page in old_data['pages']:
        page['content'] = page.pop('html')
        new_conn['pages'].insert(dict(page))
    del old_data['pages']

    print('MIGRATING Keys')
    for key in old_data['keys']:
        key['challenge_id'] = key.pop('chal')
        key['content'] = key.pop('flag')
        new_conn['flags'].insert(dict(key))
    del old_data['keys']

    print('MIGRATING Tags')
    for tag in old_data['tags']:
        tag['challenge_id'] = tag.pop('chal')
        tag['value'] = tag.pop('tag')
        new_conn['tags'].insert(dict(tag))
    del old_data['tags']

    print('MIGRATING Files')
    for f in old_data['files']:
        challenge_id = f.pop('chal')
        if challenge_id:
            f['challenge_id'] = challenge_id
            f['type'] = 'challenge'
        else:
            f['page_id'] = None
            f['type'] = 'page'
        new_conn['files'].insert(dict(f))
    del old_data['files']

    print('MIGRATING Hints')
    for hint in old_data['hints']:
        hint['type'] = 'standard'
        hint['challenge_id'] = hint.pop('chal')
        hint['content'] = hint.pop('hint')
        new_conn['hints'].insert(dict(hint))
    del old_data['hints']

    print('MIGRATING Unlocks')
    for unlock in old_data['unlocks']:
        unlock['user_id'] = unlock.pop('teamid')  # This is intentional as previous CTFds are effectively in user mode
        unlock['target'] = unlock.pop('item_id')
        unlock['type'] = unlock.pop('model')
        new_conn['unlocks'].insert(dict(unlock))
    del old_data['unlocks']

    print('MIGRATING Awards')
    for award in old_data['awards']:
        award['user_id'] = award.pop('teamid')  # This is intentional as previous CTFds are effectively in user mode
        new_conn['awards'].insert(dict(award))
    del old_data['awards']

    submissions = []
    for solve in old_data['solves']:
        solve.pop('id') # ID of a solve doesn't really matter
        solve['challenge_id'] = solve.pop('chalid')
        solve['user_id'] = solve.pop('teamid')
        solve['provided'] = solve.pop('flag')
        solve['type'] = 'correct'
        solve['model'] = 'solve'
        submissions.append(solve)

    for wrong_key in old_data['wrong_keys']:
        wrong_key.pop('id') # ID of a fail doesn't really matter.
        wrong_key['challenge_id'] = wrong_key.pop('chalid')
        wrong_key['user_id'] = wrong_key.pop('teamid')
        wrong_key['provided'] = wrong_key.pop('flag')
        wrong_key['type'] = 'incorrect'
        wrong_key['model'] = 'wrong_key'
        submissions.append(wrong_key)

    submissions = sorted(submissions, key=lambda k: k['date'])
    print('MIGRATING Solves & WrongKeys')
    for submission in submissions:
        model = submission.pop('model')
        if model == 'solve':
            new_id = new_conn['submissions'].insert(dict(submission))
            submission['id'] = new_id
            new_conn['solves'].insert(dict(submission))
        elif model == 'wrong_key':
            new_conn['submissions'].insert(dict(submission))
    del old_data['solves']
    del old_data['wrong_keys']

    print('MIGRATING Tracking')
    for tracking in old_data['tracking']:
        tracking['user_id'] = tracking.pop('team')
        new_conn['tracking'].insert(dict(tracking))
    del old_data['tracking']

    print('MIGRATING Config')
    banned = [
        'ctf_version',
        'setup'
    ]
    for config in old_data['config']:
        config.pop('id')
        if config['key'] not in banned:
            new_conn['config'].insert(dict(config))
    new_conn['config'].insert({
        'key': 'user_mode',
        'value': 'users'
    })
    del old_data['config']

    print('MIGRATING extra tables')
    for table in old_data.keys():
        print('MIGRATING', table)
        data = old_data[table]
        for row in data:
            new_conn[table].insert(dict(row))
