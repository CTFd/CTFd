from tests.helpers import (create_ctfd,
                           destroy_ctfd,
                           register_user,
                           login_as_user)


def test_get_admin_statistics():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/statistics')
        assert r.status_code == 200
    destroy_ctfd(app)
