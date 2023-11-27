#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import create_ctfd, destroy_ctfd, gen_award, gen_team, login_as_user


def test_api_team_place_score_hidden_if_scores_hidden():
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
            assert resp["data"]["score"] == 100

        set_config("score_visibility", "hidden")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/me", json="")
            resp = r.get_json()
            # Teams can see their own score but they cannot see their place
            # This is because a team can always sum up their own score but
            # they cannot determine their place without social information
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] == 100

        set_config("score_visibility", "admins")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/me", json="")
            resp = r.get_json()
            # The same behavior as above applies even under admins only score mode
            # The rationale is the same. Teams can always sum their own score
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] == 100

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            print(resp)
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] == 100
    destroy_ctfd(app)


def test_api_public_team_place_score_hidden_if_scores_hidden():
    """/api/v1/teams/<team_id> should not reveal team place if scores aren't visible"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        app.db.session.commit()

        gen_award(app.db, user_id=2, team_id=1)

        u = Users.query.filter_by(id=2).first()

        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["place"] is not None

        set_config("score_visibility", "hidden")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] is None

        set_config("score_visibility", "admins")
        with login_as_user(app, name=u.name) as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] is None

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/teams/1", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] is not None
    destroy_ctfd(app)
