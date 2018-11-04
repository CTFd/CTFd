from tests.helpers import *


def test_get_admin_pages():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_pages_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages/new')
        assert r.status_code == 200
    destroy_ctfd(app)
