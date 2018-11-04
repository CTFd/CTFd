from tests.helpers import *


def test_get_admin_users():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/users')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_users_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/users/new')
        assert r.status_code == 200
    destroy_ctfd(app)
