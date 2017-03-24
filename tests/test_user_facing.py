from tests.helpers import create_ctfd, register_user, login_as_user, gen_challenge
from CTFd.models import Teams
import json


def test_index():
    """Does the index page return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200


def test_register_user():
    """Can a user can be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user


def test_register_duplicate_teamname():
    """A user shouldn't be able to use and already registered team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user


def test_register_duplicate_email():
    """A user shouldn't be able to use an already registered email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user2", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user


def test_user_bad_login():
    """A user should not be able to login with an incorrect password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user", password="wrong_password")
        r = client.get('/profile')
        assert r.location.startswith("http://localhost/login")  # We got redirected to login


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.location != "http://localhost/login"  # We didn't get redirected to login
        assert r.status_code == 200


def test_user_isnt_admin():
    """A registered user cannot access admin pages"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/admin/graphs')
        assert r.location == "http://localhost/login"
        assert r.status_code == 302


def test_user_get_teams():
    """Can a registered user can load /teams"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/teams')
        assert r.status_code == 200


def test_user_get_scoreboard():
    """Can a registered user can load /scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scoreboard')
        assert r.status_code == 200


def test_user_get_scores():
    """Can a registered user can load /scores"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scores')
        assert r.status_code == 200


def test_user_get_topteams():
    """Can a registered user can load /top/10"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/top/10')
        assert r.status_code == 200


def test_user_get_challenges():
    """Can a registered user can load /challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/challenges')
        assert r.status_code == 200


def test_user_get_chals():
    """Can a registered user can load /chals"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals')
        assert r.status_code == 200


def test_user_get_solves_per_chal():
    """Can a registered user can load /chals/solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals/solves')
        assert r.status_code == 200


def test_user_get_solves():
    """Can a registered user can load /solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/solves')
        assert r.status_code == 200


def test_user_get_team_page():
    """Can a registered user can load their public profile (/team/2)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/team/2')
        assert r.status_code == 200


def test_user_get_profile():
    """Can a registered user can load their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.status_code == 200


def test_user_get_logout():
    """Can a registered user load /logout"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        client.get('/logout', follow_redirects=True)
        r = client.get('/challenges')
        assert r.location == "http://localhost/login?next=challenges"
        assert r.status_code == 302


def test_user_get_reset_password():
    """Can an unregistered user load /reset_password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = app.test_client()
        r = client.get('/reset_password')
        assert r.status_code == 200


def test_viewing_challenges():
    """Test that users can see added challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get('/chals')
        chals = json.loads(r.get_data(as_text=True))
        assert len(chals['game']) == 1
