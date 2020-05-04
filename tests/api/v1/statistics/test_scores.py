#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_api_statistics_score_distribution():
    app = create_ctfd()
    with app.app_context():
        # Handle zero data case
        client = login_as_user(app, name="admin", password="password")
        r = client.get("/api/v1/statistics/scores/distribution")
        resp = r.get_json()
        assert resp["data"]["brackets"] == {}

        # Add user data
        register_user(app)
        user = Users.query.filter_by(email="user@ctfd.io").first()
        simulate_user_activity(app.db, user=user)

        # Test again
        r = client.get("/api/v1/statistics/scores/distribution")
        resp = r.get_json()
        assert resp["data"]["brackets"]
    destroy_ctfd(app)
