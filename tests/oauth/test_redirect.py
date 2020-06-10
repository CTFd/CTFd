#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    login_with_mlc,
    register_user,
)


def test_oauth_not_configured():
    """Test that OAuth redirection fails if OAuth settings aren't configured"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/oauth", follow_redirects=False)
            assert r.location == "http://localhost/login"
            r = client.get(r.location)
            resp = r.get_data(as_text=True)
            assert "OAuth Settings not configured" in resp
    destroy_ctfd(app)


def test_oauth_configured_flow():
    """Test that MLC integration works properly but does not allow registration (account creation) if disabled"""
    app = create_ctfd(user_mode="teams")
    app.config.update(
        {
            "OAUTH_CLIENT_ID": "ctfd_testing_client_id",
            "OAUTH_CLIENT_SECRET": "ctfd_testing_client_secret",
            "OAUTH_AUTHORIZATION_ENDPOINT": "http://auth.localhost/oauth/authorize",
            "OAUTH_TOKEN_ENDPOINT": "http://auth.localhost/oauth/token",
            "OAUTH_API_ENDPOINT": "http://api.localhost/user",
        }
    )
    with app.app_context():
        set_config("registration_visibility", "private")
        assert Users.query.count() == 1
        assert Teams.query.count() == 0

        client = login_with_mlc(app, raise_for_error=False)

        assert Users.query.count() == 1

        # Users shouldn't be able to register because registration is disabled
        resp = client.get("http://localhost/login").get_data(as_text=True)
        assert "Public registration is disabled" in resp

        set_config("registration_visibility", "public")
        client = login_with_mlc(app)

        # Users should be able to register now
        assert Users.query.count() == 2
        user = Users.query.filter_by(email="user@ctfd.io").first()
        assert user.oauth_id == 1337
        assert user.team_id == 1

        # Teams should be created
        assert Teams.query.count() == 1
        team = Teams.query.filter_by(id=1).first()
        assert team.oauth_id == 1234

        client.get("/logout")

        # Users should still be able to login if registration is disabled
        set_config("registration_visibility", "private")
        client = login_with_mlc(app)
        with client.session_transaction() as sess:
            assert sess["id"]
            assert sess["nonce"]
            assert sess["hash"]
    destroy_ctfd(app)


def test_oauth_login_upgrade():
    """Test that users who use MLC after having registered will be associated with their MLC account"""
    app = create_ctfd(user_mode="teams")
    app.config.update(
        {
            "OAUTH_CLIENT_ID": "ctfd_testing_client_id",
            "OAUTH_CLIENT_SECRET": "ctfd_testing_client_secret",
            "OAUTH_AUTHORIZATION_ENDPOINT": "http://auth.localhost/oauth/authorize",
            "OAUTH_TOKEN_ENDPOINT": "http://auth.localhost/oauth/token",
            "OAUTH_API_ENDPOINT": "http://api.localhost/user",
        }
    )
    with app.app_context():
        register_user(app)
        assert Users.query.count() == 2
        set_config("registration_visibility", "private")

        # Users should still be able to login
        client = login_as_user(app)
        client.get("/logout")

        user = Users.query.filter_by(id=2).first()
        assert user.oauth_id is None
        assert user.team_id is None

        login_with_mlc(app)

        assert Users.query.count() == 2

        # Logging in with MLC should insert an OAuth ID and team ID
        user = Users.query.filter_by(id=2).first()
        assert user.oauth_id
        assert user.verified
        assert user.team_id
    destroy_ctfd(app)
