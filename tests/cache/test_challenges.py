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


def test_adding_challenge_clears_cache():
    """
    Test that when we add a challenge, it appears in our challenge list
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        with login_as_user(app) as client, login_as_user(
            app, name="admin", password="password"
        ) as admin:
            req = client.get("/api/v1/challenges")
            data = req.get_json()
            assert data["data"] == []

            challenge_data = {
                "name": "name",
                "category": "category",
                "description": "description",
                "value": 100,
                "state": "visible",
                "type": "standard",
            }

            r = admin.post("/api/v1/challenges", json=challenge_data)
            assert r.get_json().get("data")["id"] == 1

            req = client.get("/api/v1/challenges")
            data = req.get_json()
            assert data["data"] != []
    destroy_ctfd(app)


def test_deleting_challenge_clears_cache_solves():
    """
    Test that deleting a challenge clears the cached solves for the challenge
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user)
        with login_as_user(app) as client, login_as_user(
            app, name="admin", password="password"
        ) as admin:
            req = client.get("/api/v1/challenges")
            data = req.get_json()["data"]
            challenge = data[0]
            assert challenge["solves"] == 1
            from CTFd.utils.challenges import (  # noqa: I001
                get_solve_counts_for_challenges,
                get_solves_for_challenge_id,
            )

            solves = get_solves_for_challenge_id(1)
            solve_counts = get_solve_counts_for_challenges()
            solves_req = client.get("/api/v1/challenges/1/solves").get_json()["data"]
            assert len(solves_req) == 1
            assert len(solves) == 1
            assert solve_counts[1] == 1

            r = admin.delete("/api/v1/challenges/1", json="")
            assert r.status_code == 200

            solve_counts = get_solve_counts_for_challenges()
            solves = get_solves_for_challenge_id(1)
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 404
            assert len(solves) == 0
            assert solve_counts.get(1) is None
    destroy_ctfd(app)


def test_deleting_solve_clears_cache():
    """
    Test that deleting a solve clears out the solve count cache
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user)
        with login_as_user(app) as client, login_as_user(
            app, name="admin", password="password"
        ) as admin:
            req = client.get("/api/v1/challenges")
            data = req.get_json()["data"]
            challenge = data[0]
            assert challenge["solves"] == 1
            from CTFd.utils.challenges import (  # noqa: I001
                get_solve_counts_for_challenges,
                get_solves_for_challenge_id,
            )

            solves = get_solves_for_challenge_id(1)
            solve_counts = get_solve_counts_for_challenges()
            solves_req = client.get("/api/v1/challenges/1/solves").get_json()["data"]
            assert len(solves_req) == 1
            assert len(solves) == 1
            assert solve_counts[1] == 1

            r = admin.get("/api/v1/submissions/6", json="")
            assert r.get_json()["data"]["type"] == "correct"
            r = admin.delete("/api/v1/submissions/6", json="")
            assert r.status_code == 200
            r = admin.get("/api/v1/submissions/6", json="")
            assert r.status_code == 404

            solve_counts = get_solve_counts_for_challenges()
            solves = get_solves_for_challenge_id(1)
            solves_req = client.get("/api/v1/challenges/1/solves").get_json()["data"]
            assert len(solves_req) == 0
            assert len(solves) == 0
            assert solve_counts.get(1) is None
    destroy_ctfd(app)
