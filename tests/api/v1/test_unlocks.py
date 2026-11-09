#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from unittest.mock import patch

import pytest
from redis.exceptions import ConnectionError

from CTFd.cache import cache, clear_challenges
from CTFd.config import TestingConfig
from CTFd.models import Awards, HintUnlocks, Unlocks, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
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


def test_api_unlock_locked_while_another_unlock_is_processed():
    """Test that an account cannot unlock while another unlock is being processed"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            cache.add("unlock_lock_2", 1, timeout=30)
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 403
            assert r.get_json()["success"] is False
            assert Unlocks.query.count() == 0

            cache.delete("unlock_lock_2")
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            assert Unlocks.query.count() == 1
            # Lock is released after the unlock is processed
            assert cache.get("unlock_lock_2") is None
    destroy_ctfd(app)


@pytest.mark.parametrize(
    "same_hint,points",
    [
        # Different hints with only enough points for one exercises the score check
        (False, 10),
        # The same hint with plenty of points exercises the existing unlock check
        (True, 100),
    ],
)
def test_api_unlock_hints_race(same_hint, points):
    """Test that concurrent unlocks cannot unlock more hints than the account can pay for"""

    class RedisConfig(TestingConfig):
        REDIS_URL = "redis://localhost:6379/1"
        CACHE_REDIS_URL = "redis://localhost:6379/1"
        CACHE_TYPE = "redis"

    try:
        app = create_ctfd(config=RedisConfig)
    except ConnectionError:
        print("Failed to connect to redis. Skipping test.")
        return

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        destroy_ctfd(app)
        pytest.skip(
            "Race requires a concurrent database backend (TESTING_DATABASE_URL)"
        )
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        worker_count = 8
        if same_hint:
            hint_ids = [gen_hint(app.db, challenge_id=1, cost=10).id] * worker_count
        else:
            hint_ids = [
                gen_hint(app.db, challenge_id=1, cost=10).id
                for _ in range(worker_count)
            ]
        user_id = Users.query.filter_by(name="user").first().id
        gen_award(app.db, user_id=user_id, value=points)

        session_cookie = next(
            cookie.value for cookie in client.cookie_jar if cookie.name == "session"
        )

        release = threading.Barrier(worker_count)
        statuses = []
        lock = threading.Lock()

        def worker(hint_id):
            with app.app_context(), app.test_client() as tclient:
                tclient.set_cookie("localhost", "session", session_cookie)
                release.wait(timeout=10)
                # Retry while another unlock holds the lock like a persistent client would
                for _ in range(200):
                    r = tclient.post(
                        "/api/v1/unlocks", json={"target": hint_id, "type": "hints"}
                    )
                    if "already being processed" not in r.get_data(as_text=True):
                        break
                with lock:
                    statuses.append(r.status_code)

        threads = [
            threading.Thread(target=worker, args=(hint_id,)) for hint_id in hint_ids
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=60)

        assert not any(thread.is_alive() for thread in threads)
        assert len(statuses) == worker_count

        # Exactly one unlock goes through and is paid for exactly once
        assert statuses.count(200) == 1
        assert statuses.count(400) == worker_count - 1
        assert Unlocks.query.count() == 1
        assert Awards.query.filter(Awards.value < 0).count() == 1
        app.db.session.expire_all()
        user = Users.query.filter_by(id=user_id).first()
        assert user.get_score(admin=True) == points - 10
    destroy_ctfd(app)


@pytest.mark.parametrize(
    "same_hint,points",
    [
        # The previous lock holder spent the points needed for this hint
        (False, 10),
        # The previous lock holder already unlocked this hint
        (True, 100),
    ],
)
def test_api_unlock_sees_unlocks_committed_before_acquiring_lock(same_hint, points):
    """Test that an unlock re-reads the database after acquiring the lock so that it sees what the previous
    lock holder committed even if its transaction started before that commit (REPEATABLE READ databases)"""
    app = create_ctfd()
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        destroy_ctfd(app)
        pytest.skip("Requires a concurrent database backend (TESTING_DATABASE_URL)")
    with app.app_context():
        register_user(app)
        gen_challenge(app.db)
        first = gen_hint(app.db, challenge_id=1, cost=10).id
        second = first if same_hint else gen_hint(app.db, challenge_id=1, cost=10).id
        user_id = Users.query.filter_by(name="user").first().id
        gen_award(app.db, user_id=user_id, value=points)

        def previous_lock_holder():
            # Commit an unlock from another connection like a concurrent request would
            with app.app_context():
                app.db.session.add(
                    HintUnlocks(user_id=user_id, team_id=None, target=first)
                )
                app.db.session.add(Awards(user_id=user_id, name="hint", value=-10))
                app.db.session.commit()

        add = cache.add

        def add_after_previous_lock_holder(*args, **kwargs):
            # The request has already read from the database at this point
            thread = threading.Thread(target=previous_lock_holder)
            thread.start()
            thread.join()
            return add(*args, **kwargs)

        with login_as_user(app) as client:
            with patch.object(cache, "add", side_effect=add_after_previous_lock_holder):
                r = client.post(
                    "/api/v1/unlocks", json={"target": second, "type": "hints"}
                )
            assert r.status_code == 400

        assert Unlocks.query.count() == 1
        assert Awards.query.filter(Awards.value < 0).count() == 1
    destroy_ctfd(app)


def test_api_unlock_teams_mode_requires_team():
    """Test that a user without a team cannot unlock in teams mode"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        gen_hint(app.db, challenge_id=1, cost=10)
        register_user(app)

        with login_as_user(app) as client:
            for target in (1, 2):
                r = client.post(
                    "/api/v1/unlocks", json={"target": target, "type": "hints"}
                )
                assert r.status_code == 403
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)
