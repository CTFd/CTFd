#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils.scores import get_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_team,
    gen_user,
    login_as_user,
)


def test_challenge_team_submit():
    """Is a user's solved challenge reflected by other team members"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        second_user = gen_user(app.db, name="user", email="second@ctfd.io")
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
        assert standings[0][2] == "team_name"
        assert standings[0][3] == 100
    destroy_ctfd(app)
