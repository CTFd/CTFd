#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import create_ctfd, destroy_ctfd, gen_award, gen_team, login_as_user


def test_api_team_place_hidden_if_scores_hidden():
    """/api/v1/teams/me should not reveal team place if scores aren't visible"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        app.db.session.commit()

        gen_award(app.db, user_id=2, team_id=1)

        u = Users.query.filter_by(id=2).first()

        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"

        set_config("score_visibility", "hidden")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None

        set_config("score_visibility", "admins")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            print(resp)
            assert resp["data"]["place"] == "1st"
    destroy_ctfd(app)
