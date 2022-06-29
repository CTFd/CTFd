#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Users, db
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
)


def test_banned_team():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db, banned=True)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        db.session.commit()

        client = login_as_user(app)

        routes = ["/", "/challenges", "/api/v1/challenges"]
        for route in routes:
            r = client.get(route)
            assert r.status_code == 403
    destroy_ctfd(app)


def test_teams_join_get():
    """Can a user get /teams/join"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/teams/join")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_teams_join_post():
    """Can a user post /teams/join"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        gen_team(app.db, name="team")
        with login_as_user(app) as client:
            r = client.get("/teams/join")
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/join", data=data)
            assert r.status_code == 302

            # Cannot join a team with an incorrect password
            incorrect_data = data
            incorrect_data["password"] = ""
            r = client.post("/teams/join", data=incorrect_data)
            assert r.status_code == 403
    destroy_ctfd(app)


def test_teams_join_when_already_on_team():
    """Test that a user cannot join another team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        gen_team(app.db, email="team1@examplectf.com", name="team1")
        gen_team(app.db, email="team2@examplectf.com", name="team2")
        with login_as_user(app) as client:
            r = client.get("/teams/join")
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {
                    "name": "team1",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/join", data=data)
            assert r.status_code == 302

            # Try to join another team while on a team
            r = client.get("/teams/join")
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {
                    "name": "team2",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/join", data=data)
            assert r.status_code == 403
            user = Users.query.filter_by(name="user").first()
            assert user.team.name == "team1"
    destroy_ctfd(app)


def test_team_login():
    """Can a user login as a team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db, name="user")
        team = gen_team(app.db)
        user.team_id = team.id
        team.members.append(user)
        app.db.session.commit()
        with login_as_user(app) as client:
            r = client.get("/team")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_team_join_ratelimited():
    """Test that team joins are ratelimited"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        gen_team(app.db, name="team")
        with login_as_user(app) as client:
            r = client.get("/teams/join")
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "wrong_password",
                    "nonce": sess.get("nonce"),
                }
            for _ in range(10):
                r = client.post("/teams/join", data=data)

            data["password"] = "password"
            for _ in range(10):
                r = client.post("/teams/join", data=data)
                assert r.status_code == 429
                assert Users.query.filter_by(id=2).first().team_id is None
    destroy_ctfd(app)


def test_teams_new_get():
    """Can a user get /teams/new"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/teams/new")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_teams_new_post():
    """Can a user post /teams/new"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        with login_as_user(app) as client:
            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/new", data=data)
            assert r.status_code == 302

            # You can't create a team with a duplicate name
            r = client.post("/teams/new", data=data)
            assert r.status_code == 403

            # You can't create a team with an empty name
            incorrect_data = data
            incorrect_data["name"] = ""
            r = client.post("/teams/new", data=incorrect_data)
            assert r.status_code == 403
    destroy_ctfd(app)


def test_teams_new_post_when_already_on_team():
    """Test that a user cannot create a new team while on a team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        with login_as_user(app) as client:
            with client.session_transaction() as sess:
                data = {
                    "name": "team1",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/new", data=data)
            assert r.status_code == 302

            # Try to create another team while on a team
            r = client.get("/teams/new")
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {
                    "name": "team2",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/join", data=data)
            assert r.status_code == 403
            user = Users.query.filter_by(name="user").first()
            assert user.team.name == "team1"
    destroy_ctfd(app)


def test_teams_from_admin_hidden():
    """Test that teams created by admins in /teams/new are hidden by default"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        with login_as_user(app) as client:
            with client.session_transaction() as sess:
                data = {
                    "name": "team_user",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/new", data=data)
            assert r.status_code == 302

            team = Teams.query.filter_by(name="team_user").first()
            assert team.hidden == False

        with login_as_user(app, "admin") as client:
            with client.session_transaction() as sess:
                data = {
                    "name": "team_admin",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/new", data=data)
            assert r.status_code == 302

            team = Teams.query.filter_by(name="team_admin").first()
            assert team.hidden == True
    destroy_ctfd(app)
