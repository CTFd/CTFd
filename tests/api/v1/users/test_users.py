#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users, db
from CTFd.utils.crypto import verify_password
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_api_self_ban():
    """PATCH /api/v1/users/<user_id> should not allow a user to ban themselves"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            r = client.patch("/api/v1/users/1", json={"banned": True})
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["success"] == False
            assert resp["errors"] == {"id": "You cannot ban yourself"}
    destroy_ctfd(app)


def test_api_modify_user_type():
    """Can a user patch /api/v1/users/<user_id> to promote a user to admin and demote them to user"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, "admin") as client:
            r = client.patch("/api/v1/users/2", json={"type": "admin"})
            assert r.status_code == 200
            user_data = r.get_json()["data"]
            assert user_data["name"] == "user"
            assert user_data["type"] == "admin"

            r = client.patch("/api/v1/users/2", json={"type": "user"})
            assert r.status_code == 200
            user_data = r.get_json()["data"]
            assert user_data["name"] == "user"
            assert user_data["type"] == "user"
    destroy_ctfd(app)


def test_api_can_query_by_user_emails():
    """Can an admin user query /api/v1/users using a user's email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="testuser", email="user@findme.com")
        with login_as_user(app, "testuser") as client:
            r = client.get("/api/v1/users?field=email&q=findme", json=True)
            assert r.status_code == 400
            assert r.get_json()["errors"].get("field")
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/users?field=email&q=findme", json=True)
            assert r.status_code == 200
            assert r.get_json()["data"][0]["id"] == 2
    destroy_ctfd(app)


def test_api_user_can_update_password_if_none_not_if_set():
    """Can a user set their password if they do not currently have a password"""
    app = create_ctfd()
    with app.app_context():
        # Create a user with a null password. Use raw SQL to bypass SQLAlchemy validates
        register_user(app, name="testuser", email="user@examplectf.com")
        db.session.execute("UPDATE users SET password=NULL WHERE name='testuser'")
        user = Users.query.filter_by(name="testuser").first()
        db.session.commit()
        assert user.password is None

        with app.test_client() as client:
            # Login as user
            with client.session_transaction() as sess:
                sess["id"] = user.id
            r = client.get("/api/v1/users/me", json=True)
            assert r.status_code == 200

            # Test that user can change password
            user = Users.query.filter_by(name="testuser").first()
            assert user.password is None
            data = {"password": "12345", "confirm": "password"}
            r = client.patch("/api/v1/users/me", json=data)
            assert r.status_code == 200

            # Verify password is now set
            user = Users.query.filter_by(name="testuser").first()
            assert verify_password(plaintext="12345", ciphertext=user.password)

            # Verify that password cannot be changed
            data = {"password": "noset", "confirm": "password"}
            r = client.patch("/api/v1/users/me", json=data)
            resp = r.get_json()
            assert resp["errors"]["confirm"] == ["Your previous password is incorrect"]
            assert r.status_code == 400

            # Verify a regular user cannot patch another user
            register_user(
                app,
                name="testuser2",
                email="user2@examplectf.com",
                password="testinguser",
            )
            testuser = Users.query.filter_by(name="testuser2").first()
            assert verify_password(
                plaintext="testinguser", ciphertext=testuser.password
            )
            data = {"password": "password", "confirm": "password"}
            r = client.patch("/api/v1/users/3", json=data)
            assert r.status_code == 403
            testuser = Users.query.filter_by(name="testuser2").first()
            assert verify_password(
                plaintext="testinguser", ciphertext=testuser.password
            )

    destroy_ctfd(app)
