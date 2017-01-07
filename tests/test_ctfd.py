from helpers import create_ctfd, register_user, login_as_user
from CTFd.models import Teams


def test_index():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200


def test_register_user():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user


def test_user_isnt_admin():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/admin/graphs')
        assert r.location == "http://localhost/login"
        assert r.status_code == 302
