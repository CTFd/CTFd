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
