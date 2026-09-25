#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.cache import clear_challenges
from CTFd.models import Awards, Unlocks
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_hint,
    gen_solution,
    gen_solve,
    login_as_user,
    register_user,
)


def test_api_unlock_ignores_forged_ip():
    """Test that a user cannot forge the IP address stored in an Unlock"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/unlocks",
                json={"target": 1, "type": "hints", "ip": "198.51.100.99"},
                environ_base={"REMOTE_ADDR": "203.0.113.10"},
            )
            assert r.status_code == 200

            unlock = Unlocks.query.first()
            assert unlock.ip == "203.0.113.10"
            assert r.get_json()["data"]["ip"] == "203.0.113.10"
    destroy_ctfd(app)


def test_api_unlock_hint_hidden_challenge():
    """Test that a user cannot unlock a hint for a hidden challenge"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, state="hidden")
        gen_hint(app.db, challenge_id=1, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 404

        assert Unlocks.query.count() == 0
        assert Awards.query.count() == 0
    destroy_ctfd(app)


def test_api_unlock_hint_challenge_prerequisites():
    """Test that a user cannot unlock a hint for a challenge with unmet prerequisites"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_challenge(
            app.db,
            name="gated",
            requirements={"prerequisites": [1], "anonymize": True},
        )
        gen_hint(app.db, challenge_id=2, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 403
            assert Unlocks.query.count() == 0
            assert Awards.query.count() == 0

            gen_solve(app.db, user_id=2, challenge_id=1)
            clear_challenges()

            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            assert Unlocks.query.count() == 1
    destroy_ctfd(app)


def test_api_unlock_hint_prerequisites():
    """Test that a user cannot unlock a hint with unmet hint prerequisites"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        gen_hint(app.db, challenge_id=1, cost=0, requirements={"prerequisites": [1]})
        register_user(app)

        with login_as_user(app) as client:
            r = client.post("/api/v1/unlocks", json={"target": 2, "type": "hints"})
            assert r.status_code == 403
            assert Unlocks.query.count() == 0

            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            r = client.post("/api/v1/unlocks", json={"target": 2, "type": "hints"})
            assert r.status_code == 200
            assert Unlocks.query.count() == 2
    destroy_ctfd(app)


def test_api_unlock_solution_hidden_challenge():
    """Test that a user cannot unlock a solution for a hidden challenge"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, state="hidden")
        gen_solution(app.db, challenge_id=1, state="visible")
        register_user(app)

        with login_as_user(app) as client:
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "solutions"})
            assert r.status_code == 404

        assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_api_unlock_admin_hidden_challenge():
    """Test that an admin can unlock a hint for a hidden challenge"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, state="hidden")
        gen_hint(app.db, challenge_id=1, cost=0)

        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_unlock_invalid_request():
    """Test that malformed unlock requests return 400"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            for data in (
                {},
                {"type": "hints"},
                {"target": 1},
                {"target": 1, "type": "users"},
                {"target": 1, "type": "nonexistent"},
            ):
                r = client.post("/api/v1/unlocks", json=data)
                assert r.status_code == 400

        assert Unlocks.query.count() == 0
    destroy_ctfd(app)
