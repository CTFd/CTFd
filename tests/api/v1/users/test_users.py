#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
