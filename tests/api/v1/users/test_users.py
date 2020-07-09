#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import create_ctfd, destroy_ctfd, login_as_user


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
