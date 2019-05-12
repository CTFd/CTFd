#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import get_config
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user


def test_api_configs_get_non_admin():
    """Can a user get /api/v1/configs if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/configs")
            assert r.status_code == 302

            # test_api_configs_post_non_admin
            """Can a user post /api/v1/configs if not admin"""
            r = client.post("/api/v1/configs", json="")
            assert r.status_code == 403

            # test_api_configs_patch_non_admin
            """Can a user patch /api/v1/configs if not admin"""
            r = client.patch("/api/v1/configs", json="")
            assert r.status_code == 403

            # test_api_config_get_non_admin
            """Can a user get /api/v1/configs/<config_key> if not admin"""
            r = client.get("/api/v1/configs/ctf_name")
            assert r.status_code == 302

            # test_api_config_patch_non_admin
            """Can a user patch /api/v1/configs/<config_key> if not admin"""
            r = client.patch("/api/v1/configs/ctf_name", json="")
            assert r.status_code == 403

            # test_api_config_delete_non_admin
            """Can a user delete /api/v1/configs/<config_key> if not admin"""
            r = client.delete("/api/v1/configs/ctf_name", json="")
            assert r.status_code == 403
            assert get_config("ctf_name") == "CTFd"
    destroy_ctfd(app)


def test_api_configs_get_admin():
    """Can a user get /api/v1/configs if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.get("/api/v1/configs")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_configs_post_admin():
    """Can a user post /api/v1/configs if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.post("/api/v1/configs", json={"value": "9.9.9", "key": "test"})
            assert r.status_code == 200
            assert get_config("test") == "9.9.9"
    destroy_ctfd(app)


def test_api_configs_patch_admin():
    """Can a user patch /api/v1/configs if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.patch("/api/v1/configs", json={"ctf_name": "Changed_Name"})
            assert r.status_code == 200
            assert get_config("ctf_name") == "Changed_Name"
    destroy_ctfd(app)


def test_api_config_get_admin():
    """Can a user get /api/v1/configs/<config_key> if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.get("/api/v1/configs/ctf_name")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_config_patch_admin():
    """Can a user patch /api/v1/configs/<config_key> if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.patch("/api/v1/configs/ctf_name", json={"value": "Changed_Name"})
            assert r.status_code == 200
            assert get_config("ctf_name") == "Changed_Name"
    destroy_ctfd(app)


def test_api_config_delete_admin():
    """Can a user delete /api/v1/configs/<config_key> if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            r = admin.delete("/api/v1/configs/ctf_name", json="")
            assert r.status_code == 200
            assert get_config("ctf_name") is None
    destroy_ctfd(app)
