#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time

from CTFd.models import Unlocks, Users, db
from CTFd.utils import set_config, text_type
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_flag,
    gen_hint,
    login_as_user,
    register_user,
)


def test_user_cannot_unlock_hint():
    """Test that a user can't unlock a hint if they don't have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client():
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            gen_flag(app.db, challenge_id=chal.id, content="flag")

            hint = gen_hint(db, chal_id, cost=10)
            hint_id = hint.id

            client = login_as_user(app, name="user1", password="password")

            with client.session_transaction():
                r = client.get("/api/v1/hints/{}".format(hint_id))
                resp = r.get_json()
                assert resp["data"].get("content") is None
                assert resp["data"].get("cost") == 10
    destroy_ctfd(app)


def test_user_can_unlock_hint():
    """Test that a user can unlock a hint if they have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client():
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            gen_flag(app.db, challenge_id=chal.id, content="flag")

            hint = gen_hint(app.db, chal_id, cost=10)
            hint_id = hint.id

            gen_award(app.db, user_id=2, value=15)

            client = login_as_user(app, name="user1", password="password")

            user = Users.query.filter_by(name="user1").first()
            assert user.score == 15

            with client.session_transaction():
                r = client.get("/api/v1/hints/{}".format(hint_id))
                resp = r.get_json()
                assert resp["data"].get("content") is None

                params = {"target": hint_id, "type": "hints"}

                r = client.post("/api/v1/unlocks", json=params)
                resp = r.get_json()
                assert resp["success"] is True

                r = client.get("/api/v1/hints/{}".format(hint_id))
                resp = r.get_json()
                assert resp["data"].get("content") == "This is a hint"

                user = Users.query.filter_by(name="user1").first()
                assert user.score == 5
    destroy_ctfd(app)


def test_unlocking_hints_with_no_cost():
    """Test that hints with no cost can be unlocked"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_hint(app.db, chal_id)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        resp = r.get_json()["data"]
        assert resp.get("content") == "This is a hint"
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_ctf_with_points():
    """Test that hints with a cost are unlocked if you have the points"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_hint(app.db, chal_id, cost=10)
        gen_award(app.db, user_id=2)

        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.get_json()["data"].get("content") is None

        client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})

        r = client.get("/api/v1/hints/1")
        assert r.get_json()["data"].get("content") == "This is a hint"

        user = Users.query.filter_by(id=2).first()
        assert user.score == 90
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_ctf_without_points():
    """Test that hints with a cost are not unlocked if you don't have the points"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_hint(app.db, chal_id, cost=10)

        client = login_as_user(app)

        r = client.get("/api/v1/hints/1")
        assert r.get_json()["data"].get("content") is None

        r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
        assert (
            r.get_json()["errors"]["score"]
            == "You do not have enough points to unlock this hint"
        )

        r = client.get("/api/v1/hints/1")
        assert r.get_json()["data"].get("content") is None

        user = Users.query.filter_by(id=2).first()
        assert user.score == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_before_ctf():
    """Test that hints are not unlocked if the CTF hasn't begun"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_hint(app.db, chal_id)
        gen_award(app.db, user_id=2)

        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-1"):
            client = login_as_user(app)

            r = client.get("/api/v1/hints/1")
            assert r.status_code == 403
            assert r.get_json().get("data") is None

            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 403
            assert r.get_json().get("data") is None

            r = client.get("/api/v1/hints/1")
            assert r.get_json().get("data") is None
            assert r.status_code == 403

            user = Users.query.filter_by(id=2).first()

            assert user.score == 100
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_ended_ctf():
    """Test that hints with a cost are not unlocked if the CTF has ended"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_hint(app.db, chal_id, cost=10)
        gen_award(app.db, user_id=2)

        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-11-4"):
            client = login_as_user(app)

            r = client.get("/api/v1/hints/1")
            assert r.get_json().get("data") is None
            assert r.status_code == 403

            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 403
            assert r.get_json()

            r = client.get("/api/v1/hints/1")
            assert r.status_code == 403

            user = Users.query.filter_by(id=2).first()
            assert user.score == 100
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_frozen_ctf():
    """Test that hints with a cost are unlocked if the CTF is frozen."""
    app = create_ctfd()
    with app.app_context():
        set_config(
            "freeze", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        with freeze_time("2017-10-4"):
            register_user(app)
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_hint(app.db, chal_id, cost=10)
            gen_award(app.db, user_id=2)

        with freeze_time("2017-10-8"):
            client = login_as_user(app)

            client.get("/api/v1/hints/1")

            client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})

            r = client.get("/api/v1/hints/1")

            resp = r.get_json()["data"]
            assert resp.get("content") == "This is a hint"

            user = Users.query.filter_by(id=2).first()
            assert user.score == 100
    destroy_ctfd(app)


def test_unlocking_hint_for_unicode_challenge():
    """Test that hints for challenges with unicode names can be unlocked"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db, name=text_type("🐺"))
        chal_id = chal.id
        gen_hint(app.db, chal_id)

        client = login_as_user(app)

        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("content") == "This is a hint"
    destroy_ctfd(app)
