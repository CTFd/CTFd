#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils.scores import get_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_hint,
    gen_team,
    gen_user,
    login_as_user,
)


def test_hint_team_unlock():
    """Is a user's unlocked hint reflected on other team members"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        second_user = gen_user(app.db, name="user", email="second@ctfd.io")
        team = gen_team(app.db)
        user.team_id = team.id
        second_user.team_id = team.id
        team.members.append(user)
        team.members.append(second_user)
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="hint", cost=1, type="standard")
        gen_award(app.db, 2, team.id)
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            client.get("/api/v1/hints/1")
            client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            client.get("/api/v1/hints/1")
        with login_as_user(app) as second_client:
            second_client.get("/api/v1/hints/1")
            second_client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            r = second_client.get("/api/v1/hints/1")
            assert r.json["data"]["content"] == "hint"
            standings = get_standings()
            assert standings[0][2] == "team_name"
            assert standings[0][3] == 99
    destroy_ctfd(app)
