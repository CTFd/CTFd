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


def test_scoreboard_team_score():
    """Is a user's submitted flag reflected on the team's score on /scoreboard"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db, name="user")
        team = gen_team(app.db)
        user.team_id = team.id
        team.members.append(user)
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        app.db.session.commit()
        with login_as_user(app) as client:
            flag = {"challenge_id": 1, "submission": "flag"}
            client.post("/api/v1/challenges/attempt", json=flag)
        standings = get_standings()
        assert standings[0].name == "team_name"
        assert standings[0].score == 100
    destroy_ctfd(app)
