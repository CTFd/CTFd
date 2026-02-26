import datetime

import pyotp

from CTFd.models import Users, UsersMFA
from CTFd.utils.security.auth import generate_user_token
from CTFd.utils.security.mfa import encrypt_totp_secret, hash_backup_codes
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_login_requires_mfa_when_enabled():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(name="user").first()

        secret = pyotp.random_base32()
        mfa = UsersMFA(
            user_id=user.id,
            enabled=True,
            totp_secret=encrypt_totp_secret(secret),
            backup_codes=hash_backup_codes(["BACKUPCODE"]),
        )
        app.db.session.add(mfa)
        app.db.session.commit()

        with app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                nonce = sess.get("nonce")

            r = client.post(
                "/login",
                data={"name": "user", "password": "password", "nonce": nonce},
                follow_redirects=False,
            )
            assert r.status_code == 302
            assert r.location == "/login"

            with client.session_transaction() as sess:
                assert sess.get("mfa_pending") is True
                nonce = sess.get("nonce")

            r = client.get("/profile")
            assert r.status_code == 302
            assert r.location.startswith("/login")

            otp = pyotp.TOTP(secret).now()
            r = client.post(
                "/login",
                data={"mfa_code": otp, "mfa_backup_code": "", "nonce": nonce},
                follow_redirects=False,
            )
            assert r.status_code == 302
            assert r.location == "/challenges"

    destroy_ctfd(app)


def test_api_tokens_work_with_mfa_enabled():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(name="user").first()

        secret = pyotp.random_base32()
        mfa = UsersMFA(
            user_id=user.id,
            enabled=True,
            totp_secret=encrypt_totp_secret(secret),
            backup_codes=hash_backup_codes(["BACKUPCODE"]),
        )
        app.db.session.add(mfa)
        app.db.session.commit()

        token = generate_user_token(
            user,
            expiration=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        )
        headers = {"Authorization": "token " + token.value}

        with app.test_client() as client:
            r = client.get("/api/v1/users/me", headers=headers, json="")
            assert r.status_code == 200

    destroy_ctfd(app)


def test_api_token_generation_allowed_with_api_token_when_mfa_enabled():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(name="user").first()

        secret = pyotp.random_base32()
        mfa = UsersMFA(
            user_id=user.id,
            enabled=True,
            totp_secret=encrypt_totp_secret(secret),
            backup_codes=hash_backup_codes(["BACKUPCODE"]),
        )
        app.db.session.add(mfa)
        app.db.session.commit()

        token = generate_user_token(
            user,
            expiration=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        )
        headers = {"Authorization": "Token " + token.value}

        with app.test_client() as client:
            r = client.post("/api/v1/tokens", headers=headers, json={})
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["value"]

    destroy_ctfd(app)


def test_session_token_generation_requires_otp_when_mfa_enabled():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(name="user").first()

        secret = pyotp.random_base32()
        mfa = UsersMFA(
            user_id=user.id,
            enabled=True,
            totp_secret=encrypt_totp_secret(secret),
            backup_codes=hash_backup_codes(["BACKUPCODE"]),
        )
        app.db.session.add(mfa)
        app.db.session.commit()

        with app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                nonce = sess.get("nonce")

            r = client.post(
                "/login",
                data={"name": "user", "password": "password", "nonce": nonce},
                follow_redirects=False,
            )
            assert r.status_code == 302
            assert r.location == "/login"

            with client.session_transaction() as sess:
                nonce = sess.get("nonce")

            login_otp = pyotp.TOTP(secret).now()
            r = client.post(
                "/login",
                data={"mfa_code": login_otp, "mfa_backup_code": "", "nonce": nonce},
                follow_redirects=False,
            )
            assert r.status_code == 302
            assert r.location == "/challenges"

            r = client.post("/api/v1/tokens", json={})
            assert r.status_code == 400
            data = r.get_json()
            assert data["errors"]["mfa_code"]

            token_otp = pyotp.TOTP(secret).now()
            r = client.post("/api/v1/tokens", json={"mfa_code": token_otp})
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["value"]

    destroy_ctfd(app)


def test_user_can_enable_mfa_from_settings():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)

        r = client.post(
            "/api/v1/users/me/mfa/setup",
            json={},
        )
        assert r.status_code == 200

        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["enrolling"] is True
        assert data["data"]["qrcode"]
        secret = data["data"]["secret"]

        otp = pyotp.TOTP(secret).now()
        r = client.post(
            "/api/v1/users/me/mfa/enable",
            json={
                "confirm": "password",
                "mfa_code": otp,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["enabled"] is True
        assert len(data["data"]["backup_codes"]) == 10

        user = Users.query.filter_by(name="user").first()
        assert user.mfa is not None
        assert user.mfa.enabled is True

    destroy_ctfd(app)
