#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
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
        user = Users.query.filter_by(email="user@examplectf.com").first()
        simulate_user_activity(app.db, user=user)

        # Test again
        r = client.get("/api/v1/statistics/scores/distribution")
        resp = r.get_json()
        assert resp["data"]["brackets"]
    destroy_ctfd(app)


def test_browse_admin_submissions():
    """Test that an admin can create a challenge properly"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(db=app.db)
        admin = login_as_user(app, name="admin", password="password")
        r = admin.get(
            "/api/v1/statistics/challenges/category?function=sum&target=value"
        )
        resp = r.get_json()
        assert resp["data"]
        assert r.status_code == 200
    destroy_ctfd(app)
