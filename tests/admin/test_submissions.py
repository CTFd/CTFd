from tests.helpers import *


def test_get_admin_submissions():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions_correct():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions/correct')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions_incorrect():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions/incorrect')
        assert r.status_code == 200
    destroy_ctfd(app)
