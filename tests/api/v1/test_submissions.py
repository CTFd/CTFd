#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Discards, Fails, Solves
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_fail,
    gen_solve,
    gen_team,
    login_as_user,
    register_user,
)


def test_api_submissions_get_non_admin():
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_solve(app.db, user_id=1)
        with app.test_client() as client:
            # test_api_submissions_get_non_admin
            """Can a user get /api/v1/submissions if not admin"""
            r = client.get("/api/v1/submissions", json="")
            assert r.status_code == 403

            # test_api_submissions_post_non_admin
            """Can a user post /api/v1/submissions if not admin"""
            r = client.post("/api/v1/submissions")
            assert r.status_code == 403

            # test_api_submission_get_non_admin
            """Can a user get /api/v1/submissions/<submission_id> if not admin"""
            r = client.get("/api/v1/submissions/1", json="")
            assert r.status_code == 403

            # test_api_submission_delete_non_admin
            """Can a user delete /api/v1/submissions/<submission_id> if not admin"""
            r = client.delete("/api/v1/submissions/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_submissions_get_admin():
    """Can a user get /api/v1/submissions if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/submissions", json="")
            assert r.status_code == 200
            r = client.get("/api/v1/submissions?user_id=1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submissions_post_admin():
    """Can a user post /api/v1/submissions if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/submissions",
                json={
                    "provided": "MARKED AS SOLVED BY ADMIN",
                    "user_id": 1,
                    "team_id": None,
                    "challenge_id": "1",
                    "type": "correct",
                },
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submission_get_admin():
    """Can a user get /api/v1/submissions/<submission_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_solve(app.db, user_id=1)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/submissions/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submission_delete_admin():
    """Can a user patch /api/v1/submissions/<submission_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_solve(app.db, user_id=1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/submissions/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
    destroy_ctfd(app)


def test_api_submission_patch_correct():
    """Test that patching a submission to correct creates a solve"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_challenge(app.db)
        gen_fail(app.db, challenge_id=1, user_id=2)
        assert Solves.query.count() == 0
        with login_as_user(app, "admin") as client:
            r = client.patch("/api/v1/submissions/1", json={"type": "correct"})
            assert r.status_code == 200
            assert Fails.query.count() == 0
            assert Solves.query.count() == 1
            assert Discards.query.count() == 1
    destroy_ctfd(app)


def test_api_submission_patch_correct_scoreboard():
    "If we adjust a submission for someone the scoreboard should be correct accounting for the time of the adjusted submission"
    app = create_ctfd()
    with app.app_context():
        # Create 2 test users
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        # Create 2 test challenges
        gen_challenge(app.db, name="chal1")
        gen_challenge(app.db, name="chal2")

        # Give the first test user only fails
        gen_fail(app.db, challenge_id=1, user_id=2)
        gen_fail(app.db, challenge_id=2, user_id=2)
        # Give the second test user only solves
        gen_solve(app.db, challenge_id=1, user_id=3)
        gen_solve(app.db, challenge_id=2, user_id=3)
        with login_as_user(app, "admin") as client:
            # user2 who has both solves should be considered on top
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 1
            assert scoreboard[0]["name"] == "user2"

            # We mark user1's first solve as correct
            # This should give them 100 points
            # It should not place them above user2 who has 200 points
            client.patch("/api/v1/submissions/1", json={"type": "correct"})
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 2
            assert scoreboard[0]["name"] == "user2"
            assert scoreboard[1]["name"] == "user1"
            assert scoreboard[1]["score"] == 100

            # We mark user1's second solve as correct
            # This should give them 200 points
            # It should place them above user2 who has 200 points but was not the first to solve the challenge
            # Based on time user1's attempts should be considered correct and first
            client.patch("/api/v1/submissions/2", json={"type": "correct"})
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 2
            assert scoreboard[0]["name"] == "user1"
            assert scoreboard[0]["score"] == 200
            assert scoreboard[1]["name"] == "user2"
            assert scoreboard[1]["score"] == 200
    destroy_ctfd(app)


def test_api_submission_patch_correct_scoreboard_teams():
    "If we adjust a submission for a team the scoreboard should be correct after the adjustment"
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        # Create 2 test teams each with only 1 user
        gen_team(app.db, name="team1", email="team1@examplectf.com", member_count=1)
        gen_team(app.db, name="team2", email="team2@examplectf.com", member_count=1)

        # Create 2 test challenges
        gen_challenge(app.db, name="chal1")
        gen_challenge(app.db, name="chal2")

        # Assign only fails to the user in team 1
        gen_fail(app.db, challenge_id=1, user_id=2, team_id=1)
        gen_fail(app.db, challenge_id=2, user_id=2, team_id=1)
        # Assign only solves to the user in team 2
        gen_solve(app.db, challenge_id=1, user_id=3, team_id=2)
        gen_solve(app.db, challenge_id=2, user_id=3, team_id=2)

        with login_as_user(app, "admin") as client:
            # team2 who has both solves should be considered on top
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 1
            assert scoreboard[0]["name"] == "team2"

            # We then convert the first submission which should give team1 100 points
            # team1 should also now appear on the scoreboard in 2nd place
            client.patch("/api/v1/submissions/1", json={"type": "correct"})
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 2
            assert scoreboard[0]["name"] == "team2"
            assert scoreboard[1]["name"] == "team1"
            assert scoreboard[1]["score"] == 100

            # We mark team1's second solve as correct
            # This should give them 200 points
            # It should place them above team2 who has 200 points but was not the first to solve the challenge
            # Based on time team1's attempts should be considered correct and first
            client.patch("/api/v1/submissions/2", json={"type": "correct"})
            scoreboard = client.get("/api/v1/scoreboard").get_json()["data"]
            assert len(scoreboard) == 2
            assert scoreboard[0]["name"] == "team1"
            assert scoreboard[0]["score"] == 200
            assert scoreboard[1]["name"] == "team2"
            assert scoreboard[1]["score"] == 200
    destroy_ctfd(app)
