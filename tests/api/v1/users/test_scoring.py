#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_api_user_place_score_hidden_if_scores_hidden():
    """/api/v1/users/me should not reveal user place if scores aren't visible"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user=user)

        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] == 200

        set_config("score_visibility", "hidden")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/me", json="")
            resp = r.get_json()
            # Users can see their own score but they cannot see their place
            # This is because a user can always sum up their own score but
            # they cannot determine their place without social information
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] == 200

        set_config("score_visibility", "admins")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/me", json="")
            resp = r.get_json()
            # The same behavior as above applies even under admins only score mode
            # The rationale is the same. Users can always sum their own score
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] == 200

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] is not None
    destroy_ctfd(app)


def test_api_public_user_place_score_hidden_if_scores_hidden():
    """/api/v1/users/<user_id> should not reveal user place if scores aren't visible"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user=user)

        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] is not None

        set_config("score_visibility", "hidden")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] is None

        set_config("score_visibility", "admins")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None
            assert resp["data"]["score"] is None

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
            assert resp["data"]["score"] is not None
    destroy_ctfd(app)
