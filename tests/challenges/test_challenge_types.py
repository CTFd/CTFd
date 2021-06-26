#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Challenges
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_missing_challenge_type():
    """Test that missing challenge types don't cause total challenge rendering failure"""
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "state": "visible",
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1
        assert r.get_json().get("data")["type"] == "dynamic"

        chal_count = Challenges.query.count()
        assert chal_count == 1

        # Delete the dynamic challenge type
        from CTFd.plugins.challenges import CHALLENGE_CLASSES

        del CHALLENGE_CLASSES["dynamic"]

        r = client.get("/admin/challenges")
        assert r.status_code == 200
        assert b"dynamic" in r.data

        r = client.get("/admin/challenges/1")
        assert r.status_code == 500
        assert b"The underlying challenge type (dynamic) is not installed" in r.data

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "visible",
            "type": "standard",
        }
        r = client.post("/api/v1/challenges", json=challenge_data)

        r = client.get("/challenges")
        assert r.status_code == 200

        # We should still see the one visible standard challenge
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        assert len(r.json["data"]) == 1
        assert r.json["data"][0]["type"] == "standard"

        # We cannot load the broken challenge
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 500
        assert (
            "The underlying challenge type (dynamic) is not installed"
            in r.json["message"]
        )

        # We can load other challenges
        r = client.get("/api/v1/challenges/2")
        assert r.status_code == 200
    destroy_ctfd(app)
