#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import jsonify
from flask_caching import make_template_fragment_key

from CTFd.cache import clear_standings
from CTFd.models import Users
from CTFd.utils.scoreboard import get_scoreboard_detail
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_flag,
    gen_solve,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
)


def test_scoreboard_is_cached():
    """Test that /api/v1/scoreboard is properly cached and cleared"""
    app = create_ctfd()
    with app.app_context():
        # create user1
        register_user(app, name="user1", email="user1@examplectf.com")

        # create challenge
        chal = gen_challenge(app.db, value=100)
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        chal_id = chal.id

        # create a solve for the challenge for user1. (the id is 2 because of the admin)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Initial get_scoreboard_detail cache key version
        saved = app.cache.get("CTFd.utils.scoreboard.get_scoreboard_detail_memver")

        with login_as_user(app, "user1") as client:
            # Check basic scoreboard data
            assert app.cache.get("view/api.scoreboard_scoreboard_list") is None
            client.get("/api/v1/scoreboard")
            assert app.cache.get("view/api.scoreboard_scoreboard_list")

            # Check detailed scoreboard data
            orig = jsonify(get_scoreboard_detail.uncached(count=10)).get_json()
            assert (
                app.cache.get("CTFd.utils.scoreboard.get_scoreboard_detail_memver")
                == saved
            )
            cached = client.get("/api/v1/scoreboard/top/10").get_json()
            assert cached["data"] == orig
            assert app.cache.get("CTFd.utils.scoreboard.get_scoreboard_detail_memver")

            # Check scoreboard page
            assert (
                app.cache.get(make_template_fragment_key("public_scoreboard_table"))
                is None
            )
            client.get("/scoreboard")
            assert app.cache.get(make_template_fragment_key("public_scoreboard_table"))

            # Empty standings and check that the cached data is gone
            clear_standings()
            assert app.cache.get("view/api.scoreboard_scoreboard_list") is None
            # Clearing an entire function bumps flask-cachings version identify instead of setting it to null
            new = app.cache.get("CTFd.utils.scoreboard.get_scoreboard_detail_memver")
            assert new != saved
            assert (
                app.cache.get(make_template_fragment_key("public_scoreboard_table"))
                is None
            )
    destroy_ctfd(app)


def test_scoreboard_tie_break_ordering_with_awards():
    """
    Test that scoreboard tie break ordering respects the addition of awards
    """
    app = create_ctfd()
    with app.app_context():
        # create user1
        register_user(app, name="user1", email="user1@examplectf.com")
        # create user2
        register_user(app, name="user2", email="user2@examplectf.com")

        chal = gen_challenge(app.db, value=100)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        chal = gen_challenge(app.db, value=200)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        # create solves for the challenges. (the user_ids are off by 1 because of the admin)
        gen_solve(app.db, user_id=2, challenge_id=1)
        gen_solve(app.db, user_id=3, challenge_id=2)

        with login_as_user(app, "user1") as client:
            r = client.get("/api/v1/scoreboard")
            resp = r.get_json()
            assert len(resp["data"]) == 2
            assert resp["data"][0]["name"] == "user2"
            assert resp["data"][0]["score"] == 200
            assert resp["data"][1]["name"] == "user1"
            assert resp["data"][1]["score"] == 100

        # Give user1 an award for 100 points.
        # At this point user2 should still be ahead
        gen_award(app.db, user_id=2, value=100)

        with login_as_user(app, "user1") as client:
            r = client.get("/api/v1/scoreboard")
            resp = r.get_json()
            assert len(resp["data"]) == 2
            assert resp["data"][0]["name"] == "user2"
            assert resp["data"][0]["score"] == 200
            assert resp["data"][1]["name"] == "user1"
            assert resp["data"][1]["score"] == 200
    destroy_ctfd(app)


def test_scoreboard_tie_break_ordering_with_awards_under_teams():
    """
    Test that team mode scoreboard tie break ordering respects the addition of awards
    """
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db, name="team1", email="team1@examplectf.com")
        gen_team(app.db, name="team2", email="team2@examplectf.com")

        chal = gen_challenge(app.db, value=100)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        chal = gen_challenge(app.db, value=200)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        # create solves for the challenges. (the user_ids are off by 1 because of the admin)
        gen_solve(app.db, user_id=2, team_id=1, challenge_id=1)
        gen_solve(app.db, user_id=6, team_id=2, challenge_id=2)

        user = Users.query.filter_by(id=2).first()

        with login_as_user(app, user.name) as client:
            r = client.get("/api/v1/scoreboard")
            resp = r.get_json()
            print(resp)
            assert len(resp["data"]) == 2
            assert resp["data"][0]["name"] == "team2"
            assert resp["data"][0]["score"] == 200
            assert resp["data"][1]["name"] == "team1"
            assert resp["data"][1]["score"] == 100

        # Give a user on the team an award for 100 points.
        # At this point team2 should still be ahead
        gen_award(app.db, user_id=3, team_id=1, value=100)

        with login_as_user(app, user.name) as client:
            r = client.get("/api/v1/scoreboard")
            resp = r.get_json()
            print(resp)
            assert len(resp["data"]) == 2
            assert resp["data"][0]["name"] == "team2"
            assert resp["data"][0]["score"] == 200
            assert resp["data"][1]["name"] == "team1"
            assert resp["data"][1]["score"] == 200
    destroy_ctfd(app)


def test_scoreboard_detail_returns_different_counts():
    """
    Test that /api/v1/scoreboard/top/10 and /api/v1/scoreboard/top/1
    return different amounts of values even when cached
    """
    app = create_ctfd()
    with app.app_context():
        # Create multiple users
        for i in range(2, 13):
            gen_user(app.db, name=f"user{i}", email=f"user{i}@examplectf.com")

        # Create a challenge
        chal = gen_challenge(app.db, value=100)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        # Generate solves for the challenge for multiple users
        for user_id in range(2, 13):  # User IDs start from 2 (admin is 1)
            gen_solve(app.db, user_id=user_id, challenge_id=chal.id)

        with login_as_user(app, name="user2") as client:
            # Fetch top 10 scores
            top_10_resp = client.get("/api/v1/scoreboard/top/10").get_json()
            assert len(top_10_resp["data"]) == 10

            # Fetch top 1 score
            top_1_resp = client.get("/api/v1/scoreboard/top/1").get_json()
            assert len(top_1_resp["data"]) == 1

            # Ensure the results are different
            assert top_10_resp["data"] != top_1_resp["data"]

            # Fetch scores again
            assert top_10_resp == client.get("/api/v1/scoreboard/top/10").get_json()
            assert top_1_resp == client.get("/api/v1/scoreboard/top/1").get_json()

    destroy_ctfd(app)
