from tests.helpers import *


def test_get_admin_challenges():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_challenges_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges/new')
        assert r.status_code == 200
    destroy_ctfd(app)
