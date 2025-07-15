#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Hints
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_hint,
    login_as_user,
    register_user,
)


def test_api_hint_get_non_admin():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            # test_api_hint_get_non_admin
            """Can the users get /api/v1/hints if not admin"""
            r = client.get("/api/v1/hints", json="")
            assert r.status_code == 403
            assert Hints.query.count() == 0

            # test_api_hint_post_non_admin
            """Can the users post /api/v1/hints if not admin"""
            r = client.post("/api/v1/hints", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_hint_get_admin():
    """Can the users get /api/v1/hints if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/hints", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_hint_post_admin():
    """Can the users post /api/v1/hints if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/hints", json={"content": "hint", "cost": "1", "challenge": 1}
            )
            assert r.status_code == 200
            assert Hints.query.count() == 1
    destroy_ctfd(app)


def test_admins_can_preview_hints():
    """Test that admins are able to bypass restrictions and preview hints with ?preview=true"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=100)
        client = login_as_user(app, name="admin", password="password")
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        hint = r.get_json()
        assert hint.get("content") is None

        r = client.get("/api/v1/hints/1?preview=true")
        assert r.status_code == 200
        hint = r.get_json()
        assert hint["data"]["content"] == "This is a hint"
    destroy_ctfd(app)


def test_users_cannot_preview_hints():
    """Test that users aren't able to preview hints"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=100)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/hints/1")
        assert r.status_code == 200
        hint = r.get_json()
        assert hint.get("content") is None

        r = client.get("/api/v1/hints/1?preview=true")
        assert r.status_code == 200
        hint = r.get_json()
        assert hint["data"].get("content") is None
    destroy_ctfd(app)


def test_admin_cannot_unlock_hint_with_prerequisite():
    """
    Test that admins cannot unlock hints that have a prerequisite unless the prerequisite is unlocked.
    Allow admin preview access with ?preview=true
    """
    app = create_ctfd()
    with app.app_context():
        # Create a challenge and two hints, where hint2 requires hint1 as a prerequisite
        chal = gen_challenge(app.db)
        hint1 = gen_hint(app.db, challenge_id=chal.id, content="First hint")
        hint1_id = hint1.id
        hint2 = gen_hint(
            app.db,
            challenge_id=chal.id,
            content="Second hint",
        )
        hint2.requirements = {"prerequisites": [1]}
        hint2_id = hint2.id
        app.db.session.commit()

        # Login as admin
        client = login_as_user(app, name="admin")

        # Try to access the second hint without unlocking the prerequisite
        r = client.get(f"/api/v1/hints/{hint2_id}")
        assert r.status_code == 403
        data = r.get_json()
        assert "requirements" in data.get("errors", {})

        # Try to access with preview=true (should succeed for admin)
        r = client.get(f"/api/v1/hints/{hint2_id}?preview=true")
        assert r.status_code == 200
        data = r.get_json()
        assert data["data"]["content"] == "Second hint"

        # Unlock the first hint
        r = client.post("/api/v1/unlocks", json={"target": hint1_id, "type": "hints"})
        assert r.status_code == 200

        # Now try to access the second hint (should fail b/c missing unlock)
        r = client.get(f"/api/v1/hints/{hint2_id}")
        data = r.get_json()
        assert data["data"].get("content") is None

        # Unlock the second hint
        r = client.post("/api/v1/unlocks", json={"target": hint2_id, "type": "hints"})
        assert r.status_code == 200

        # Now try to access the second hint (should succeed)
        r = client.get(f"/api/v1/hints/{hint2_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["data"]["content"] == "Second hint"
    destroy_ctfd(app)
