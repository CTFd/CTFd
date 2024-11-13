#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Users, db
from CTFd.utils.crypto import verify_password
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


def test_api_team_can_update_password_if_none_not_if_set():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        # Create a user with a null password. Use raw SQL to bypass SQLAlchemy validates
        gen_team(app.db, name="testteam", email="team@examplectf.com")
        db.session.execute("UPDATE teams SET password=NULL WHERE name='testteam'")
        team = Teams.query.filter_by(id=1).first()
        db.session.commit()
        assert team.password is None

        # Login and test that we are authed
        captain = Users.query.filter_by(id=2).first()
        normal_user = Users.query.filter_by(id=3).first()
        with login_as_user(app, captain.name) as client:
            r = client.get("/api/v1/teams/me", json=True)
            assert r.get_json()["data"]["id"] == team.id
            assert r.status_code == 200

            # Patch the team's password from NULL
            team = Teams.query.filter_by(name="testteam").first()
            assert team.password is None
            data = {"password": "12345", "confirm": "password"}
            r = client.patch("/api/v1/teams/me", json=data)
            assert r.status_code == 200

            # Verify password is now set
            team = Teams.query.filter_by(name="testteam").first()
            assert verify_password(plaintext="12345", ciphertext=team.password)

            # Verify that password cannot be changed without valid password
            data = {"password": "noset", "confirm": "noset"}
            r = client.patch("/api/v1/teams/me", json=data)
            resp = r.get_json()
            assert resp["errors"]["confirm"] == ["Your previous password is incorrect"]
            assert r.status_code == 400

            # Verify that a normal user cannot change the team password
            with login_as_user(app, normal_user.name) as client:
                # Try changing the password for the team
                data = {"password": "newpassword", "confirm": "12345"}
                r = client.patch("/api/v1/teams/me", json=data)
                assert r.status_code == 403

                # Verify that team password has not changed
                team = Teams.query.filter_by(name="testteam").first()
                assert verify_password(plaintext="12345", ciphertext=team.password)

            # Create a new team
            new_team = gen_team(app.db, name="newteam", email="newteam@examplectf.com")
            new_captain = Users.query.filter_by(id=new_team.captain_id).first()

            # Verify that the captain from the new team cannot change the password of the original team
            with login_as_user(app, new_captain.name) as client:
                data = {"password": "newpassword", "confirm": "12345"}
                r = client.patch("/api/v1/teams/1", json=data)
                assert r.status_code == 403

                # Verify that old test team password has not changed
                team = Teams.query.filter_by(name="testteam").first()
                assert verify_password(plaintext="12345", ciphertext=team.password)
