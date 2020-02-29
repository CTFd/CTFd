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


def test_api_user_place_hidden_if_scores_hidden():
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

        set_config("score_visibility", "hidden")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None

        set_config("score_visibility", "admins")
        with login_as_user(app, name="user") as client:
            r = client.get("/api/v1/users/me", json="")
            resp = r.get_json()
            assert resp["data"]["place"] is None

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/users/2", json="")
            resp = r.get_json()
            assert resp["data"]["place"] == "1st"
    destroy_ctfd(app)
