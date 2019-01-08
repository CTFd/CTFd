from tests.helpers import *


def test_sessions_set_httponly():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            cookie = dict(r.headers)['Set-Cookie']
            assert 'HttpOnly;' in cookie
    destroy_ctfd(app)


def test_sessions_set_samesite():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            cookie = dict(r.headers)['Set-Cookie']
            assert 'SameSite=' in cookie
    destroy_ctfd(app)
