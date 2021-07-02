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


def test_config_value_types():
    """Test that we properly receive values according to schema"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as admin:
            # Test new configs error out if too long
            long_text = "a" * 65536
            r = admin.post(
                "/api/v1/configs", json={"key": "new_ctf_config", "value": long_text}
            )
            data = r.get_json()
            assert data["errors"]["value"][0] == "new_ctf_config config is too long"
            assert r.status_code == 400
            r = admin.post(
                "/api/v1/configs", json={"key": "new_ctf_config", "value": "test"}
            )
            assert r.status_code == 200
            assert get_config("new_ctf_config") == "test"

            # Test strings too long error out
            r = admin.patch("/api/v1/configs", json={"ctf_footer": long_text})
            data = r.get_json()
            assert data["errors"]["value"][0] == "ctf_footer config is too long"
            assert r.status_code == 400

            # Test regular length strings
            r = admin.patch(
                "/api/v1/configs", json={"ctf_footer": "// regular length string"},
            )
            assert r.status_code == 200
            assert get_config("ctf_footer") == "// regular length string"

            # Test booleans can be received
            r = admin.patch("/api/v1/configs", json={"view_after_ctf": True})
            assert r.status_code == 200
            assert bool(get_config("view_after_ctf")) == True

            # Test None can be received
            assert get_config("mail_username") is None
            r = admin.patch("/api/v1/configs", json={"mail_username": "testusername"})
            assert r.status_code == 200
            assert get_config("mail_username") == "testusername"
            r = admin.patch("/api/v1/configs", json={"mail_username": None})
            assert r.status_code == 200
            assert get_config("mail_username") is None

            # Test integers can be received
            r = admin.patch("/api/v1/configs", json={"mail_port": 12345})
            assert r.status_code == 200
            assert get_config("mail_port") == 12345

            # Test specific config key
            r = admin.patch(
                "/api/v1/configs/long_config_test", json={"value": long_text}
            )
            data = r.get_json()
            assert data["errors"]["value"][0] == "long_config_test config is too long"
            assert r.status_code == 400
            assert get_config("long_config_test") is None
            r = admin.patch(
                "/api/v1/configs/config_test", json={"value": "config_value_test"}
            )
            assert r.status_code == 200
            assert get_config("config_test") == "config_value_test"
            r = admin.patch(
                "/api/v1/configs/mail_username", json={"value": "testusername"}
            )
            assert r.status_code == 200
            assert get_config("mail_username") == "testusername"
    destroy_ctfd(app)
