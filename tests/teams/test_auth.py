#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users, db
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
            incorrect_data = data
            incorrect_data["password"] = ""
            r = client.post("/teams/join", data=incorrect_data)
            assert r.status_code == 200
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
