#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Challenges
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_flag,
    gen_team,
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
        assert len(solves) == 1
        assert solves[0]["account_id"] == 2  # user1's ID (admin is 1)
    destroy_ctfd(app)


def test_all_flags_challenge_logic_teams_mode():
    """Test a challenge that requires all flags to be submitted for solving in teams mode"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        # Create admin for challenge creation
        admin = login_as_user(app, name="admin", password="password")

        # Create a challenge with "all" logic
        challenge_data = {
            "name": "All Flags Team Challenge",
            "category": "Logic",
            "description": "Submit all flags to solve as a team.",
            "value": 100,
            "state": "visible",
            "type": "standard",
            "logic": "all",
        }
        r = admin.post("/api/v1/challenges", json=challenge_data)
        challenge_id = r.get_json()["data"]["id"]

        c = Challenges.query.filter_by(id=challenge_id).first()
        assert c.logic == "all"

        # Create a team with members using gen_team helper
        team = gen_team(
            app.db, name="test_team", email="team@examplectf.com", member_count=3
        )
        team_id = team.id

        # Add multiple flags to the challenge
        flags = ["flag{team_one}", "flag{team_two}", "flag{team_three}"]
        for content in flags:
            gen_flag(app.db, challenge_id=challenge_id, content=content)

        # Get team members for testing
        members = team.members
        user1_name = members[0].name
        user2_name = members[1].name
        user3_name = members[2].name

        # Test that different team members can submit flags and it counts towards team progress

        # User1 submits first flag
        client1 = login_as_user(app, name=user1_name, password="password")
        submission = {"challenge_id": challenge_id, "submission": "flag{team_one}"}
        r = client1.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # User2 submits second flag
        client2 = login_as_user(app, name=user2_name, password="password")
        submission = {"challenge_id": challenge_id, "submission": "flag{team_two}"}
        r = client2.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # User3 submits third flag - should complete the challenge for the team
        client3 = login_as_user(app, name=user3_name, password="password")
        submission = {"challenge_id": challenge_id, "submission": "flag{team_three}"}
        r = client3.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "correct"

        # Check that the team is marked as having solved the challenge
        r = admin.get(f"/api/v1/challenges/{challenge_id}/solves")
        solves = r.get_json()["data"]
        assert len(solves) == 1
        assert solves[0]["account_id"] == team_id

        # Verify team score reflects the solve
        team_response = admin.get(f"/api/v1/teams/{team_id}")
        team_data = team_response.get_json()["data"]
        assert team_data["score"] == 100

        # Test that another team member trying to submit the same flag gets "already_solved"
        submission = {"challenge_id": challenge_id, "submission": "flag{team_one}"}
        r = client1.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "already_solved"

    destroy_ctfd(app)


def test_group_flags_challenge_logic_teams_mode():
    """Test a challenge that requires each team member to submit any flag for solving in teams mode"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        # Create admin for challenge creation
        admin = login_as_user(app, name="admin", password="password")

        # Create a challenge with "group" logic
        challenge_data = {
            "name": "Group Flags Team Challenge",
            "category": "Logic",
            "description": "Each team member must submit any flag to solve as a team.",
            "value": 100,
            "state": "visible",
            "type": "standard",
            "logic": "team",
        }
        r = admin.post("/api/v1/challenges", json=challenge_data)
        challenge_id = r.get_json()["data"]["id"]

        c = Challenges.query.filter_by(id=challenge_id).first()
        assert c.logic == "team"

        # Create a team with members using gen_team helper
        team = gen_team(
            app.db, name="test_team", email="team@examplectf.com", member_count=3
        )
        team_id = team.id

        # Add multiple flags to the challenge
        flags = ["flag{group_one}", "flag{group_two}", "flag{group_three}"]
        for content in flags:
            gen_flag(app.db, challenge_id=challenge_id, content=content)

        # Get team members for testing
        members = team.members
        user1_name = members[0].name
        user2_name = members[1].name
        user3_name = members[2].name

        # Test that each team member must submit any flag for the team to solve

        # User1 submits first flag - should be partial since not all members have submitted
        client1 = login_as_user(app, name=user1_name, password="password")
        submission = {"challenge_id": challenge_id, "submission": "flag{group_one}"}
        r = client1.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # User2 submits any flag (can be different) - still partial since user3 hasn't submitted
        client2 = login_as_user(app, name=user2_name, password="password")
        submission = {"challenge_id": challenge_id, "submission": "flag{group_two}"}
        r = client2.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "partial"

        # User3 submits any flag - should complete the challenge since all members have now submitted
        client3 = login_as_user(app, name=user3_name, password="password")
        submission = {
            "challenge_id": challenge_id,
            "submission": "flag{group_one}",
        }  # Can reuse same flag
        r = client3.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "correct"

        # Check that the team is marked as having solved the challenge
        r = admin.get(f"/api/v1/challenges/{challenge_id}/solves")
        solves = r.get_json()["data"]
        assert len(solves) == 1
        assert solves[0]["account_id"] == team_id

        # Verify team score reflects the solve
        team_response = admin.get(f"/api/v1/teams/{team_id}")
        team_data = team_response.get_json()["data"]
        assert team_data["score"] == 100

        # Test that team members trying to submit again get "already_solved"
        submission = {"challenge_id": challenge_id, "submission": "flag{group_three}"}
        r = client1.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "already_solved"

    destroy_ctfd(app)


def test_challenge_default_logic_is_any():
    """Test that the default logic for a challenge is 'any'"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1")
        admin = login_as_user(app, name="admin", password="password")

        # Create a challenge without specifying logic (should default to "any")
        challenge_data = {
            "name": "Default Logic Challenge",
            "category": "Test",
            "description": "Test challenge with default logic.",
            "value": 100,
            "state": "visible",
            "type": "standard",
            # Note: no "logic" field specified - should default to "any"
        }
        r = admin.post("/api/v1/challenges", json=challenge_data)
        challenge_id = r.get_json()["data"]["id"]

        # Verify the challenge logic is set to "any" by default
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        assert challenge.logic == "any"

        # Test that "any" logic works correctly
        client = login_as_user(app, name="user1", password="password")

        # Add multiple flags to the challenge
        flags = ["flag{first}", "flag{second}", "flag{third}"]
        for content in flags:
            gen_flag(app.db, challenge_id=challenge_id, content=content)

        # With "any" logic, submitting any single correct flag should solve the challenge
        submission = {"challenge_id": challenge_id, "submission": "flag{second}"}
        r = client.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "correct"

        # Verify the challenge is marked as solved
        r = admin.get(f"/api/v1/challenges/{challenge_id}/solves")
        solves = r.get_json()["data"]
        assert len(solves) == 1
        assert solves[0]["account_id"] == 2  # user1's ID (admin is 1)

        # Test that submitting another flag returns "already_solved"
        submission = {"challenge_id": challenge_id, "submission": "flag{first}"}
        r = client.post("/api/v1/challenges/attempt", json=submission)
        assert r.get_json()["data"]["status"] == "already_solved"

    destroy_ctfd(app)
