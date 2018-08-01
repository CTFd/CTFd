#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_user_can_view_challenges():
    """Test that user_can_view_challenges allows users to view challenges while not logged in"""
    app = create_ctfd()
    with app.app_context():
        set_config('view_challenges_unregistered', True)
        utils.cache.clear()  # Need to clear the cached configuration
        chal = gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 200
            r = client.get('/chals')
            assert r.status_code == 200
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('view_challenges_unregistered', False)
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 302
            r = client.get('/chals')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_verify_emails_config():
    """Test that users can only solve challenges if they are logged in and verified if verify_emails is set"""
    app = create_ctfd()
    with app.app_context():
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('verify_emails', True)
        chal = gen_challenge(app.db)

        register_user(app)
        client = login_as_user(app)

        r = client.get('/challenges')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        r = client.get('/chals')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        user = Teams.query.filter_by(id=2).first()
        user.verified = True
        app.db.session.commit()

        r = client.get('/challenges')
        assert r.status_code == 200

        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_verify_and_view_unregistered():
    """If both verify_emails and user_can_view_challenges are set, the user should see challenges while unregistered
    but be locked out if they register until they confirm their email address"""
    app = create_ctfd()
    with app.app_context():
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('view_challenges_unregistered', True)
        set_config('verify_emails', True)
        chal = gen_challenge(app.db)

        # We are not authed but we should still be able to see challenges
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 200

            r = client.get('/chals')
            assert r.status_code == 200

        # Logging in...
        register_user(app)
        client = login_as_user(app)

        # We are now logged in so we should be redirected to the confirmation page
        r = client.get('/challenges')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        r = client.get('/chals')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        user = Teams.query.filter_by(id=2).first()
        user.verified = True
        app.db.session.commit()

        # Double check that we can see challenges
        r = client.get('/challenges')
        assert r.status_code == 200

        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


@freeze_time("2019-02-24 03:21:34")
def test_expired_confirmation_links():
    """Test that expired confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config('verify_emails', True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = 'http://localhost/confirm/InVzZXJAdXNlci5jb20iLkFmS0dQZy5kLUJnVkgwaUhadzFHaXVENHczWTJCVVJwdWc'
        r = client.get(confirm_link)

        assert "Your confirmation link has expired" in r.get_data(as_text=True)
        team = Teams.query.filter_by(email='user@user.com').first()
        assert team.verified is not True
    destroy_ctfd(app)


def test_invalid_confirmation_links():
    """Test that invalid confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config('verify_emails', True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = 'http://localhost/confirm/a8375iyu<script>alert(1)<script>hn3048wueorighkgnsfg'
        r = client.get(confirm_link)

        assert "Your confirmation token is invalid" in r.get_data(as_text=True)
        team = Teams.query.filter_by(email='user@user.com').first()
        assert team.verified is not True
    destroy_ctfd(app)


@freeze_time("2019-02-24 03:21:34")
def test_expired_reset_password_link():
    """Test that expired reset password links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')

        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            # user@user.com "2012-01-14 03:21:34"
            forgot_link = 'http://localhost/reset_password/InVzZXIxIi5BZktHUGcuTVhkTmZtOWU2U2xwSXZ1MlFwTjdwa3F5V3hR'
            r = client.get(forgot_link)

            assert "Your link has expired" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_invalid_reset_password_link():
    """Test that invalid reset password links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')

        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            # user@user.com "2012-01-14 03:21:34"
            forgot_link = 'http://localhost/reset_password/5678ytfghjiu876tyfg<>hvbnmkoi9u87y6trdfcgvhbnm,lp09iujmk'
            r = client.get(forgot_link)

            assert "Your reset token is invalid" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_contact_for_password_reset():
    """Test that if there is no mailserver configured, users should contact admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            forgot_link = 'http://localhost/reset_password'
            r = client.get(forgot_link)

            assert "Contact a CTF organizer" in r.get_data(as_text=True)
    destroy_ctfd(app)
