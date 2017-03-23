from CTFd import create_app
from CTFd.models import *
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.engine.url import make_url


def create_ctfd(ctf_name="CTFd", name="admin", email="admin@ctfd.io", password="password"):
    app = create_app('CTFd.config.TestingConfig')

    url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if url.drivername == 'postgres':
        url.drivername = 'postgresql'

    if database_exists(url):
        drop_database(url)
        create_database(url)
        with app.app_context():
            app.db.create_all()

    with app.app_context():
        with app.test_client() as client:
            data = {}
            r = client.get('/setup')  # Populate session with nonce
            with client.session_transaction() as sess:
                data = {
                    "ctf_name": ctf_name,
                    "name": name,
                    "email": email,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/setup', data=data)
    return app


def register_user(app, name="user", email="user@ctfd.io", password="password"):
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/register')
            with client.session_transaction() as sess:
                data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/register', data=data)


def login_as_user(app, name="user", password="password"):
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/login')
            with client.session_transaction() as sess:
                data = {
                    "name": name,
                    "password": password,
                    "nonce": sess.get('nonce')
                }
            client.post('/login', data=data)
            return client


def gen_challenge(db, name='chal_name', description='chal_description', value=100, category='chal_category', type=0):
    chal = Challenges(name, description, value, category)
    db.session.add(chal)
    db.session.commit()
    return chal


def gen_award(db, teamid, name="award_name", value=100):
    award = Awards(teamid, name, value)
    db.session.add(award)
    db.session.commit()
    return award


def gen_tag(db, chal, tag='tag_tag'):
    tag = Tags(chal, tag)
    db.session.add(tag)
    db.session.commit()
    return tag


def gen_file():
    pass


def gen_key(db, chal, flag='flag', key_type=0):
    key = Keys(chal, flag, key_type)
    db.session.add(key)
    db.session.commit()
    return key


def gen_team(db, name='name', email='user@ctfd.io', password='password'):
    team = Teams(name, email, password)
    db.session.add(team)
    db.session.commit()
    return team


def gen_solve(db, chalid, teamid, ip='127.0.0.1', flag='rightkey'):
    solve = Solves(chalid, teamid, ip, flag)
    db.session.add(solve)
    db.session.commit()
    return solve

def gen_wrongkey(db, teamid, chalid, flag='wrongkey'):
    wrongkey = WrongKeys(teamid, chalid, flag)
    db.session.add(wrongkey)
    db.session.commit()
    return wrongkey


def gen_tracking(db, ip, team):
    tracking = Tracking(ip, team)
    db.session.add(tracking)
    db.session.commit()
    return tracking