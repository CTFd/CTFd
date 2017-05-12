from tests.helpers import create_ctfd, register_user, login_as_user
from CTFd.models import Teams


def test_admin_panel():
    """Does the admin panel return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin')
        assert r.status_code == 302
        r = client.get('/admin/graphs')
        assert r.status_code == 200


def test_admin_pages():
    """Does admin pages return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages')
        assert r.status_code == 200


def test_admin_teams():
    """Does admin teams return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/teams')
        assert r.status_code == 200


def test_admin_scoreboard():
    """Does admin scoreboard return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/scoreboard')
        assert r.status_code == 200


def test_admin_containers():
    """Does admin containers return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/containers')
        assert r.status_code == 200


def test_admin_chals():
    """Does admin chals return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/chals')
        assert r.status_code == 200


def test_admin_statistics():
    """Does admin statistics return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/statistics')
        assert r.status_code == 200


def test_admin_config():
    """Does admin config return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/config')
        assert r.status_code == 200
