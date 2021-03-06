#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time

from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_hint,
    login_as_user,
    register_user,
)


def test_api_hint_404():
    """Can the users 404 /api/v1/hints/<hint_id> if logged in/out"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_hint_visibility():
    """Can the users load /api/v1/hints/<hint_id> if logged in/out"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id)
        with app.test_client() as non_logged_in_user:
            r = non_logged_in_user.get("/api/v1/hints/1")
            assert r.status_code == 302
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_hint_visibility_ctftime():
    """Can the users load /api/v1/hints/<hint_id> if not ctftime"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_hint_locked():
    """Can the users unlock /api/v1/hints/<hint_id> if they don't have enough points"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
        assert r.status_code == 400
    destroy_ctfd(app)


def test_api_hint_unlocked():
    """Can the users unlock /api/v1/hints/<hint_id> if they have enough points"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")
        register_user(app)
        # Give user points with an award
        gen_award(app.db, 2)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
        assert r.status_code == 200
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_hint_double_unlock():
    """Can a target hint be unlocked twice"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")
        register_user(app)
        # Give user points with an award
        gen_award(app.db, 2)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
        assert r.status_code == 200
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
        assert r.status_code == 400
    destroy_ctfd(app)


def test_users_dont_prevent_other_users_from_unlocking_hints():
    """Unlocks from one user don't affect other users"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")
        register_user(app)
        register_user(app, name="user2", email="user2@examplectf.com")

        # Give users points with an award
        gen_award(app.db, user_id=2)
        gen_award(app.db, user_id=3)

        # First user unlocks hints
        with login_as_user(app) as client:
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200

        # Second user unlocks hints
        with login_as_user(app, name="user2") as client:
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_hints_admin_access():
    """Can the users access /api/v1/hints if not admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints")
        assert r.status_code == 302
        r = client.post("/api/v1/hints", json="")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_hint_admin_access():
    """Can the users patch/delete /api/v1/hint/<hint_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")
        admin = login_as_user(app, "admin")
        register_user(app)
        client = login_as_user(app)
        r = client.patch("/api/v1/hints/1", json="")
        assert r.status_code == 403
        r = client.delete("/api/v1/hints/1", json="")
        assert r.status_code == 403
        r_admin = admin.patch("/api/v1/hints/1", json={"cost": 2})
        assert r_admin.status_code == 200
        r_admin = admin.delete("/api/v1/hints/1", json="")
        assert r_admin.status_code == 200
    destroy_ctfd(app)
