#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_tag,
    login_as_user,
)


def test_api_tags_get_non_admin():
    """Can a user get /api/v1/tags if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_tag(app.db, 1)
        with app.test_client() as client:
            r = client.get("/api/v1/tags", json="")
            assert r.status_code == 403

            # test_api_tags_post_non_admin
            """Can a user post /api/v1/tags if not admin"""
            r = client.post("/api/v1/tags")
            assert r.status_code == 403

            # test_api_tag_get_non_admin
            """Can a user get /api/v1/tags/<tag_id> if not admin"""
            r = client.get("/api/v1/tags/1", json="")
            assert r.status_code == 403

            # test_api_tag_patch_non_admin
            """Can a user patch /api/v1/tags/<tag_id> if not admin"""
            r = client.patch("/api/v1/tags/1", json="")
            assert r.status_code == 403

            # test_api_tag_delete_non_admin
            """Can a user delete /api/v1/tags/<tag_id> if not admin"""
            r = client.delete("/api/v1/tags/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_tags_get_admin():
    """Can a user get /api/v1/tags if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/tags", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_tags_post_admin():
    """Can a user post /api/v1/tags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/tags", json={"value": "tag", "challenge": 1})
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_tag_get_admin():
    """Can a user get /api/v1/tags/<tag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_tag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/tags/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_tag_patch_admin():
    """Can a user patch /api/v1/tags/<tag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_tag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/tags/1", json={"value": "tag_edit", "challenge_id": 1}
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["value"] == "tag_edit"
    destroy_ctfd(app)


def test_api_tag_delete_admin():
    """Can a user patch /api/v1/tags/<tag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_tag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/tags/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
    destroy_ctfd(app)
