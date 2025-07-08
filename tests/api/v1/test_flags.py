#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Flags
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    login_as_user,
)


def test_api_flags_get_non_admin():
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)

        with app.test_client() as client:
            # test_api_flags_get_non_admin
            """Can a user get /api/v1/flags if not admin"""
            r = client.get("/api/v1/flags", json="")
            assert r.status_code == 403

            # test_api_flags_post_non_admin
            """Can a user post /api/v1/flags if not admin"""
            r = client.post("/api/v1/flags")
            assert r.status_code == 403

            # test_api_flag_types_get_non_admin
            """Can a user get /api/v1/flags/types[/<type_name>] if not admin"""
            r = client.get("/api/v1/flags/types", json="")
            assert r.status_code == 403

            # test_api_flag_get_non_admin
            """Can a user get /api/v1/flags/<flag_id> if not admin"""
            r = client.get("/api/v1/flags/1", json="")
            assert r.status_code == 403

            # test_api_flag_patch_non_admin
            """Can a user patch /api/v1/flags/<flag_id> if not admin"""
            r = client.patch("/api/v1/flags/1", json="")
            assert r.status_code == 403

            # test_api_flag_delete_non_admin
            """Can a user delete /api/v1/flags/<flag_id> if not admin"""
            r = client.delete("/api/v1/flags/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_flags_get_admin():
    """Can a user get /api/v1/flags if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/flags", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_flags_post_admin():
    """Can a user post /api/v1/flags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/flags",
                json={"content": "flag", "type": "static", "challenge": 1},
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_flag_types_get_admin():
    """Can a user get /api/v1/flags/types[/<type_name>] if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/flags/types", json="")
            assert r.status_code == 200
            r = client.get("/api/v1/flags/types/static", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_flag_get_admin():
    """Can a user get /api/v1/flags/<flag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/flags/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_flag_patch_admin():
    """Can a user patch /api/v1/flags/<flag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/flags/1",
                json={"content": "flag_edit", "data": "", "type": "static", "id": "1"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["content"] == "flag_edit"
    destroy_ctfd(app)


def test_api_flag_delete_admin():
    """Can a user patch /api/v1/flags/<flag_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/flags/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
    destroy_ctfd(app)


def test_flag_content_stripped_on_create_and_update():
    """Test that flag content is stripped of whitespace on create and update"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            # Create flag with whitespace
            r = client.post(
                "/api/v1/flags",
                json={
                    "content": "   flag_with_spaces   ",
                    "type": "static",
                    "challenge": 1,
                },
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["content"] == "flag_with_spaces"

            flag_id = data["id"]

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "flag_with_spaces"

            # Update flag with whitespace
            r = client.patch(
                f"/api/v1/flags/{flag_id}",
                json={"content": "   updated_flag   ", "type": "static"},
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["content"] == "updated_flag"

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "updated_flag"
    destroy_ctfd(app)


def test_flag_content_stripped_on_create_and_update_regex():
    """Test that regex flag content is stripped of whitespace on create and update"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            # Create regex flag with whitespace
            r = client.post(
                "/api/v1/flags",
                json={
                    "content": "   ^flag\\d+$   ",
                    "type": "regex",
                    "challenge": 1,
                },
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["content"] == "^flag\\d+$"

            flag_id = data["id"]

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "^flag\\d+$"

            # Update regex flag with whitespace
            r = client.patch(
                f"/api/v1/flags/{flag_id}",
                json={"content": "   ^updated_flag\\d+$   ", "type": "regex"},
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["content"] == "^updated_flag\\d+$"

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "^updated_flag\\d+$"


def test_flag_content_not_stripped_on_other_types():
    """Test that flag content is not stripped for non-static and non-regex types"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            # Create flag with a custom type
            r = client.post(
                "/api/v1/flags",
                json={
                    "content": "   custom_flag   ",
                    "type": "custom",
                    "challenge": 1,
                },
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            # Should not be stripped
            assert data["content"] == "   custom_flag   "

            flag_id = data["id"]

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "   custom_flag   "

            # Update flag with whitespace
            r = client.patch(
                f"/api/v1/flags/{flag_id}",
                json={"content": "   updated_custom_flag   ", "type": "custom"},
            )
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["content"] == "   updated_custom_flag   "

            f = Flags.query.filter_by(id=flag_id).first()
            assert f.content == "   updated_custom_flag   "
