#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_team,
    login_as_user,
    register_user,
)


def test_api_can_query_by_team_emails():
    """Can an admin user query /api/v1/teams using a teams's email address"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db, email="team@findme.com")
        register_user(app, name="testuser", email="user@findme.com")
        with login_as_user(app, "testuser") as client:
            r = client.get("/api/v1/teams?field=email&q=findme", json=True)
            assert r.status_code == 400
            assert r.get_json()["errors"].get("field")
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/teams?field=email&q=findme", json=True)
            assert r.status_code == 200
            assert r.get_json()["data"][0]["id"] == 1
            assert r.get_json()["data"][0]["name"] == "team_name"
    destroy_ctfd(app)
