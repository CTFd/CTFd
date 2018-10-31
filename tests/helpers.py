from CTFd import create_app
from CTFd.models import *
from CTFd.cache import cache
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.engine.url import make_url
import datetime
import six
import gc

if six.PY2:
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


def create_ctfd(ctf_name="CTFd", name="admin", email="admin@ctfd.io",
                password="password", user_mode="users", setup=True):
    app = create_app('CTFd.config.TestingConfig')

    if setup:
        app = setup_ctfd(app, ctf_name, name, email, password, user_mode)
    return app


def setup_ctfd(app, ctf_name="CTFd", name="admin",
               email="admin@ctfd.io", password="password", user_mode="users"):
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/setup')  # Populate session with nonce
            with client.session_transaction() as sess:
                data = {
                    "ctf_name": ctf_name,
                    "name": name,
                    "email": email,
                    "password": password,
                    "user_mode": user_mode,
                    "nonce": sess.get('nonce')
                }
            client.post('/setup', data=data)
    return app


def destroy_ctfd(app):
    with app.app_context():
        app.db.session.commit()
        app.db.session.close_all()
        gc.collect()  # Garbage collect (necessary in the case of dataset freezes to clean database connections)
        app.db.drop_all()
        cache.clear()
    drop_database(app.config['SQLALCHEMY_DATABASE_URI'])


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


def get_scores(user):
    scores = user.get('/scores')
    print(scores.get_data(as_text=True))
    scores = json.loads(scores.get_data(as_text=True))
    print(scores)
    return scores['standings']


def gen_challenge(db, name='chal_name', description='chal_description', value=100,
                  category='chal_category', type='standard', state='visible', **kwargs):
    chal = Challenges(
        name=name,
        description=description,
        value=value,
        category=category,
        type=type,
        state=state,
        **kwargs)
    db.session.add(chal)
    db.session.commit()
    return chal


def gen_award(db, team_id, name="award_name", value=100):
    award = Awards(team_id=team_id, name=name, value=value)
    award.date = datetime.datetime.utcnow()
    db.session.add(award)
    db.session.commit()
    return award


def gen_tag(db, challenge_id, value='tag_tag', **kwargs):
    tag = Tags(challenge_id=challenge_id, value=value, **kwargs)
    db.session.add(tag)
    db.session.commit()
    return tag


def gen_file(db, challenge_id, location):
    f = Files(challenge_id=challenge_id, location=location)
    db.session.add(f)
    db.session.commit()
    return f


def gen_flag(db, challenge_id, content='flag',
             type='static', data=None, **kwargs):
    flag = Flags(
        challenge_id=challenge_id,
        content=content,
        type=type,
        **kwargs)
    if data:
        flag.data = data
    db.session.add(flag)
    db.session.commit()
    return flag


def gen_user(db, name='user_name', email='user@ctfd.io',
             password='password', **kwargs):
    user = Users(name=name, email=email, password=password, **kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def gen_team(db, name='team_name', email='team@ctfd.io',
             password='password', **kwargs):
    team = Teams(name=name, email=email, password=password, **kwargs)
    db.session.add(team)
    db.session.commit()
    return team


def gen_hint(db, challenge_id, hint="This is a hint",
             cost=0, type=0, **kwargs):
    hint = Hints(
        challenge_id=challenge_id,
        hint=hint,
        cost=cost,
        type=type,
        **kwargs)
    db.session.add(hint)
    db.session.commit()
    return hint


def gen_solve(db, team_id, challenge_id, ip='127.0.0.1',
              flag='rightkey', **kwargs):
    solve = Solves(
        team_id=team_id,
        challenge_id=challenge_id,
        ip=ip,
        flag=flag,
        **kwargs)
    solve.date = datetime.datetime.utcnow()
    db.session.add(solve)
    db.session.commit()
    return solve


def gen_wrongkey(db, team_id, challenge_id, ip='127.0.0.1',
                 content='wrongkey', **kwargs):
    wrongkey = Fails(
        team_id=team_id,
        challenge_id=challenge_id,
        ip=ip,
        content=content)
    wrongkey.date = datetime.datetime.utcnow()
    db.session.add(wrongkey)
    db.session.commit()
    return wrongkey


def gen_tracking(db, ip, team, **kwargs):
    # TODO: This might not make sense for user mode teams
    tracking = Tracking(ip=ip, user_id=team, **kwargs)
    db.session.add(tracking)
    db.session.commit()
    return tracking


def gen_page(db, title, route, html, draft=False,
             auth_required=False, **kwargs):
    page = Pages(
        title=title,
        route=route,
        html=html,
        draft=draft,
        auth_required=auth_required,
        **kwargs)
    db.session.add(page)
    db.session.commit()
    return page
