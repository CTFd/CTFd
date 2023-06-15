from unittest.mock import Mock, patch
from uuid import UUID

from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_sessions_set_httponly():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/")
            cookie = dict(r.headers)["Set-Cookie"]
            assert "HttpOnly;" in cookie
    destroy_ctfd(app)


def test_sessions_set_samesite():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/")
            cookie = dict(r.headers)["Set-Cookie"]
            assert "SameSite=" in cookie
    destroy_ctfd(app)


def test_session_invalidation_on_admin_password_change():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, name="admin") as admin, login_as_user(app) as user:

            r = user.get("/settings")
            assert r.status_code == 200

            r = admin.patch("/api/v1/users/2", json={"password": "password2"})
            assert r.status_code == 200

            r = user.get("/settings")
            # User's password was changed
            # They should be logged out
            assert r.location.startswith("http://localhost/login")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_session_invalidation_on_user_password_change():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as user:

            r = user.get("/settings")
            assert r.status_code == 200

            data = {"confirm": "password", "password": "new_password"}

            r = user.patch("/api/v1/users/me", json=data)
            assert r.status_code == 200

            r = user.get("/settings")
            # User initiated their own password change
            # They should not be logged out
            assert r.status_code == 200
    destroy_ctfd(app)


# @patch.object(uuid, 'uuid4', side_effect=TEST_UUIDS)
# @patch.object(uuid, 'uuid4')
def test_session_with_duplicate_session_id():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        register_user(app, name="user1", email="user1@examplectf.com")

        TEST_UUIDS = [
            # First user login successful
            UUID("2d0ac3a8-b956-491a-9f53-d27cd33f2529"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            # Second user gets a unique UUID then a duplicated one
            UUID("c47c907f-d508-4f23-a28a-a1af1e9d3f27"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            UUID("85e61378-5bc4-4cc8-a37e-b03270b7b172"),
            # Second user should finally receive a unique UUID
            UUID("a00aff35-a12e-465a-8747-e18f78f60b13"),
            UUID("da876038-7602-4bb0-88b8-f7104094219f"),
        ]
        uuid_mock = Mock(side_effect=TEST_UUIDS)

        with patch(target="CTFd.utils.sessions.uuid4", new=uuid_mock):
            login_as_user(app)
        with patch(target="CTFd.utils.sessions.uuid4", new=uuid_mock):
            login_as_user(app, name="user1")
    destroy_ctfd(app)
