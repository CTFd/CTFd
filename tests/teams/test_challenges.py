#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from CTFd.utils.scores import get_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
)


def test_challenge_team_submit():
    """Is a user's solved challenge reflected by other team members"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        second_user = gen_user(app.db, name="user", email="second@examplectf.com")
        team = gen_team(app.db)
        user.team_id = team.id
        second_user.team_id = team.id
        team.members.append(user)
        team.members.append(second_user)
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            flag = {"challenge_id": 1, "submission": "flag"}
            client.post("/api/v1/challenges/attempt", json=flag)
        with login_as_user(app) as second_client:
            flag = {"challenge_id": 1, "submission": "flag"}
            r = second_client.post("/api/v1/challenges/attempt", json=flag)
            assert r.json["data"]["status"] == "already_solved"
        standings = get_standings()
        assert standings[0].name == "team_name"
        assert standings[0].score == 100
    destroy_ctfd(app)


def test_anonymous_users_view_public_challenges_without_team():
    """Test that if challenges are public, users without team can still view them"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/challenges")
            assert r.status_code == 302
            assert r.location.startswith("http://localhost/login")

        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            r = client.get("/challenges")
            assert r.status_code == 200

        with login_as_user(app) as client:
            r = client.get("/challenges")
            assert r.status_code == 302
            assert r.location.startswith("http://localhost/team")
    destroy_ctfd(app)
