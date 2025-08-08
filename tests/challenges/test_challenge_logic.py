#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_flag,
    login_as_user,
    register_user,
)


def test_all_flags_challenge_logic():
    """Test a challenge that requires all flags to be submitted for solving"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1")
        admin = login_as_user(app, name="admin", password="password")

        # Create a challenge
        challenge_data = {
            "name": "All Flags Challenge",
            "category": "Logic",
            "description": "Submit all flags to solve.",
            "value": 100,
            "state": "visible",
            "type": "standard",
            "logic": "all",
        }
        r = admin.post("/api/v1/challenges", json=challenge_data)
        challenge_id = r.get_json()["data"]["id"]

        client = login_as_user(app, name="user1", password="password")

        # Add multiple flags to the challenge
        flags = ["flag{one}", "flag{two}", "flag{three}"]
        for content in flags:
            gen_flag(app.db, challenge_id=challenge_id, content=content)

        # Simulate "all flags" logic: user must submit all flags to solve
        # Submit only one flag
        submission = {"challenge_id": challenge_id, "submission": "flag{one}"}
        r = client.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # Submit two flags (simulate by submitting them one after another)
        submission = {"challenge_id": challenge_id, "submission": "flag{two}"}
        r = client.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # Submit all three flags
        submission = {"challenge_id": challenge_id, "submission": "flag{three}"}
        r = client.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "correct"

        # After all flags are submitted, the challenge should be marked as solved
        r = client.get(f"/api/v1/challenges/{challenge_id}/solves")
        solves = r.get_json()["data"]
        print(solves)
        assert len(solves) == 1
        assert solves[0]["account_id"] == 2  # user1's ID (admin is 1)
    destroy_ctfd(app)
