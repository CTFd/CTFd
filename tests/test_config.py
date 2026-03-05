#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.exceptions import SecurityError

from CTFd.config import TestingConfig
from CTFd.models import Configs, Users, db
from CTFd.utils import get_config
from CTFd.utils.crypto import verify_password
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_user,
    login_as_user,
    register_user,
)


def test_reverse_proxy_config():
    """Test that REVERSE_PROXY configuration behaves properly"""

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = "1,2,3,4"

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 2
        assert app.wsgi_app.x_host == 3
        assert app.wsgi_app.x_port == 4
        assert app.wsgi_app.x_prefix == 0
    destroy_ctfd(app)

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = "true"

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 1
        assert app.wsgi_app.x_host == 1
        assert app.wsgi_app.x_port == 1
        assert app.wsgi_app.x_prefix == 1
    destroy_ctfd(app)

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = True

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 1
        assert app.wsgi_app.x_host == 1
        assert app.wsgi_app.x_port == 1
        assert app.wsgi_app.x_prefix == 1
    destroy_ctfd(app)


def test_server_sent_events_config():
    """Test that SERVER_SENT_EVENTS configuration behaves properly"""

    class ServerSentEventsConfig(TestingConfig):
        SERVER_SENT_EVENTS = False

    app = create_ctfd(config=ServerSentEventsConfig)
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/events")
        assert r.status_code == 204
    destroy_ctfd(app)


def test_trusted_hosts_config():
    """Test that TRUSTED_HOSTS configuration behaves properly"""

    class TrustedHostsConfig(TestingConfig):
        SERVER_NAME = "example.com"
        TRUSTED_HOSTS = ["example.com"]

    app = create_ctfd(config=TrustedHostsConfig)
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/", headers={"Host": "example.com"})
        assert r.status_code == 200

        # TODO: We need to allow either a 500 or a 400 because Flask-RestX
        # seems to be overriding Flask's error handler
        try:
            r = client.get("/", headers={"Host": "evil.com"})
        except SecurityError:
            pass
        else:
            if r.status_code != 400:
                raise SecurityError("Responded to untrusted request")
    destroy_ctfd(app)


def test_preset_admin_config():
    """Test that PRESET_ADMIN configuration allows login and creates admin user"""

    class PresetAdminConfig(TestingConfig):
        PRESET_ADMIN_NAME = "preset_admin"
        PRESET_ADMIN_EMAIL = "preset@example.com"
        PRESET_ADMIN_PASSWORD = "preset_password_123"

    app = create_ctfd(config=PresetAdminConfig)
    with app.app_context():
        # Verify no preset admin exists initially
        preset_admin = Users.query.filter_by(name="preset_admin").first()
        assert preset_admin is None

        # Attempt login with incorrect preset admin credentials via name
        client = app.test_client()
        login_data = {"name": "preset_admin", "password": "wrong_preset_password_123"}
        # Get login page first to get nonce
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)
        assert r.status_code == 200
        assert "incorrect" in r.get_data(as_text=True)
        preset_admin = Users.query.filter_by(name="preset_admin").first()
        assert preset_admin is None

        # Attempt login with preset admin credentials via name
        client = app.test_client()
        login_data = {"name": "preset_admin", "password": "preset_password_123"}
        # Get login page first to get nonce
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)

        # Should redirect to challenges page after successful login
        assert r.status_code == 302
        assert "/challenges" in r.location or r.location.endswith("/")

        # Verify admin user was created
        preset_admin = Users.query.filter_by(name="preset_admin").first()
        assert preset_admin is not None
        assert preset_admin.email == "preset@example.com"
        assert preset_admin.type == "admin"
        assert preset_admin.verified is True

        assert verify_password("preset_password_123", preset_admin.password) is True

        # Test login via email as well
        client = app.test_client()
        login_data = {"name": "preset@example.com", "password": "preset_password_123"}
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)
        assert r.status_code == 302

        # Test that wrong password fails
        client = app.test_client()
        login_data = {"name": "preset_admin", "password": "wrong_password"}
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)
        # Should return login page with error, not redirect
        assert r.status_code == 200
        assert b"incorrect" in r.data.lower() or b"invalid" in r.data.lower()

        assert Users.query.filter_by(type="admin").count() == 2

    destroy_ctfd(app)


def test_preset_admin_token_config():
    """Test that PRESET_ADMIN_TOKEN allows API access and creates admin user"""

    class PresetAdminTokenConfig(TestingConfig):
        PRESET_ADMIN_NAME = "preset_token_admin"
        PRESET_ADMIN_EMAIL = "preset_token@example.com"
        PRESET_ADMIN_PASSWORD = "preset_token_password_123"
        PRESET_ADMIN_TOKEN = "preset_secret_token_12345"

    app = create_ctfd(config=PresetAdminTokenConfig)
    with app.app_context():
        # Verify no preset admin exists initially
        preset_admin = Users.query.filter_by(name="preset_token_admin").first()
        assert preset_admin is None

        # Test that wrong token fails
        client = app.test_client()
        wrong_headers = {
            "Authorization": "Token wrong_token_123",
            "Content-Type": "application/json",
        }
        r = client.get("/api/v1/users/me", headers=wrong_headers)
        assert r.status_code in [401, 403]  # Should be unauthorized

        # Test API access without authentication (should fail)
        client = app.test_client()
        r = client.get("/api/v1/users/me", json=True)
        assert r.status_code in [401, 403]  # Unauthorized or Forbidden

        # Test API access with preset admin token
        headers = {
            "Authorization": "Token preset_secret_token_12345",
            "Content-Type": "application/json",
        }
        r = client.get("/api/v1/users/me", headers=headers, json=True)

        # Should succeed and create the admin user
        assert r.status_code == 200

        # Verify admin user was created
        preset_admin = Users.query.filter_by(name="preset_token_admin").first()
        assert preset_admin is not None
        assert preset_admin.email == "preset_token@example.com"
        assert preset_admin.type == "admin"
        assert preset_admin.verified is True

        assert (
            verify_password("preset_token_password_123", preset_admin.password) is True
        )

        # Verify the API response contains the admin user information
        response_data = r.get_json()

        assert response_data["success"] is True
        assert response_data["data"]["name"] == "preset_token_admin"
        assert response_data["data"]["email"] == "preset_token@example.com"

        # Check that we are admin
        r = client.get("/api/v1/challenges/types", headers=headers, json=True)
        assert r.status_code == 200

        # Test that wrong token fails
        wrong_headers = {
            "Authorization": "Token wrong_token_123",
            "Content-Type": "application/json",
        }
        r = client.get("/api/v1/users/me", headers=wrong_headers, json=True)
        assert r.status_code in [401, 403]  # Should be unauthorized

        assert Users.query.filter_by(type="admin").count() == 2

    destroy_ctfd(app)


def test_preset_admin_no_promotion_existing_user():
    """Test that existing regular users with preset credentials don't get promoted to admin"""

    class PresetAdminConfig(TestingConfig):
        PRESET_ADMIN_NAME = "existing_user"
        PRESET_ADMIN_EMAIL = "existing@example.com"
        PRESET_ADMIN_PASSWORD = "preset_password_123"

    app = create_ctfd(config=PresetAdminConfig)
    with app.app_context():
        # Create a regular user with the same credentials as preset admin
        gen_user(
            app.db,
            name="existing_user",
            email="existing@example.com",
            password="preset_password_123",
            type="user",  # Regular user, not admin
        )

        # Verify user exists and is not admin
        user = Users.query.filter_by(name="existing_user").first()
        assert user is not None
        assert user.type == "user"
        assert user.email == "existing@example.com"

        # Attempt login with preset admin credentials
        client = app.test_client()
        login_data = {"name": "existing_user", "password": "preset_password_123"}
        # Get login page first to get nonce
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)

        # Should fail in logging in
        assert r.status_code == 200
        assert (
            "Preset admin user could not be created. Please contact an administrator"
            in r.get_data(as_text=True)
        )

        # Test that the user is not an admin
        r = client.get("/api/v1/challenges/types", json=True)
        assert r.status_code in [
            401,
            403,
        ]  # Should be unauthorized/forbidden for regular user

        # Verify user is still not admin (no promotion)
        user = Users.query.filter_by(name="existing_user").first()
        assert user is not None
        assert user.type == "user"  # Should still be regular user
        assert user.email == "existing@example.com"

        # Also test login via email
        client = app.test_client()
        login_data = {"name": "existing@example.com", "password": "preset_password_123"}
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)
        # Should fail in logging in
        assert r.status_code == 200
        assert (
            "Preset admin user could not be created. Please contact an administrator"
            in r.get_data(as_text=True)
        )

        # Test that the user is not an admin
        r = client.get("/api/v1/challenges/types", json=True)
        assert r.status_code in [
            401,
            403,
        ]  # Should be unauthorized/forbidden for regular user

        # User should still be regular user after email login
        user = Users.query.filter_by(name="existing_user").first()
        assert user.type == "user"

        # Verify only one admin exists (the default setup admin)
        admin_count = Users.query.filter_by(type="admin").count()
        assert admin_count == 1

    destroy_ctfd(app)


def test_preset_admin_empty_credentials():
    """Test that empty preset credentials don't allow login"""

    # Test empty password
    class PresetAdminEmptyPasswordConfig(TestingConfig):
        PRESET_ADMIN_NAME = "preset_admin_empty"
        PRESET_ADMIN_EMAIL = "preset_empty@example.com"
        PRESET_ADMIN_PASSWORD = ""  # Empty password

    app = create_ctfd(config=PresetAdminEmptyPasswordConfig)
    with app.app_context():
        # Verify no preset admin exists initially
        preset_admin = Users.query.filter_by(name="preset_admin_empty").first()
        assert preset_admin is None

        # Attempt login with empty password (should fail)
        client = app.test_client()
        login_data = {"name": "preset_admin_empty", "password": ""}
        client.get("/login")
        with client.session_transaction() as sess:
            login_data["nonce"] = sess.get("nonce")
        r = client.post("/login", data=login_data)

        # Should not create user or allow login
        assert r.status_code == 200
        assert "incorrect" in r.get_data(as_text=True).lower()

        # Verify no admin user was created
        preset_admin = Users.query.filter_by(name="preset_admin_empty").first()
        assert preset_admin is None

    destroy_ctfd(app)

    # Test empty token
    class PresetAdminEmptyTokenConfig(TestingConfig):
        PRESET_ADMIN_NAME = "preset_admin_empty_token"
        PRESET_ADMIN_EMAIL = "preset_empty_token@example.com"
        PRESET_ADMIN_PASSWORD = "some_password"
        PRESET_ADMIN_TOKEN = ""  # Empty token

    app = create_ctfd(config=PresetAdminEmptyTokenConfig)
    with app.app_context():
        # Verify no preset admin exists initially
        preset_admin = Users.query.filter_by(name="preset_admin_empty_token").first()
        assert preset_admin is None

        # Test API access with empty token (should fail)
        client = app.test_client()
        empty_headers = {
            "Authorization": "Token  ",
            "Content-Type": "application/json",
        }
        r = client.get("/api/v1/users/me", headers=empty_headers)
        assert r.status_code in [401, 403]  # Should be unauthorized

        # Test API access without Authorization header (should also fail)
        r = client.get("/api/v1/users/me", json=True)
        assert r.status_code in [401, 403]  # Should be unauthorized

        # Verify no admin user was created
        preset_admin = Users.query.filter_by(name="preset_admin_empty_token").first()
        assert preset_admin is None

    destroy_ctfd(app)


def test_preset_configs():
    """Test that PRESET_CONFIGS are loaded and accessible via get_config"""

    class PresetConfigsConfig(TestingConfig):
        PRESET_CONFIGS = {
            "ctf_name": "Test CTF Name",
            "ctf_description": "This is a test CTF description",
            "user_mode": "users",
            "challenge_visibility": "public",
            "registration_visibility": "public",
            "score_visibility": "public",
            "account_visibility": "public",
            "custom_setting": "custom_value_123",
        }

    app = create_ctfd(config=PresetConfigsConfig)
    with app.app_context():
        # Test that preset configs are accessible via get_config
        assert get_config("ctf_name") == "Test CTF Name"
        assert get_config("ctf_description") == "This is a test CTF description"
        assert get_config("user_mode") == "users"
        assert get_config("challenge_visibility") == "public"
        assert get_config("registration_visibility") == "public"
        assert get_config("score_visibility") == "public"
        assert get_config("account_visibility") == "public"
        assert get_config("custom_setting") == "custom_value_123"

        # Test that non-existent config returns None (or default)
        assert get_config("non_existent_config") is None
        assert (
            get_config("non_existent_config", default="default_value")
            == "default_value"
        )

        # Add a database config that conflicts with a preset config
        db_config = Configs(key="ctf_name", value="Database CTF Name")
        db.session.add(db_config)
        db.session.commit()

        # The preset config should still take precedence (not overridden by database)
        assert get_config("ctf_name") == "Test CTF Name"

        # Test that database configs work for keys not in PRESET_CONFIGS
        db_config_new = Configs(key="database_only_setting", value="database_value")
        db.session.add(db_config_new)
        db.session.commit()

        # This should come from the database since it's not in presets
        assert get_config("database_only_setting") == "database_value"

    destroy_ctfd(app)
