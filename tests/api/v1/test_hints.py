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
