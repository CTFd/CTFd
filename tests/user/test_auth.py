#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config, get_config
from freezegun import freeze_time
from tests.helpers import *


def test_register_user():
    """Can a user be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_register_unicode_user():
    """Can a user with a unicode name be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="你好")
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_register_duplicate_username():
    """A user shouldn't be able to use an already registered team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_register_duplicate_email():
    """A user shouldn't be able to use an already registered email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user2", email="user1@ctfd.io", password="password")
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_user_bad_login():
    """A user should not be able to login with an incorrect password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user", password="wrong_password")
        with client.session_transaction() as sess:
            assert sess.get('id') is None
        r = client.get('/profile')
        assert r.location.startswith("http://localhost/login")  # We got redirected to login
    destroy_ctfd(app)


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.location != "http://localhost/login"  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_login_with_email():
    """Can a registered user can login with an email address instead of a team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user@ctfd.io", password="password")
        r = client.get('/profile')
        assert r.location != "http://localhost/login"  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_isnt_admin():
    """A registered user cannot access admin pages"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        for page in ['pages', 'users', 'teams', 'scoreboard', 'challenges', 'statistics', 'config']:
            r = client.get('/admin/{}'.format(page))
            assert r.location.startswith("http://localhost/login?next=")
            assert r.status_code == 302
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
        user = Users.query.filter_by(email='user@user.com').first()
        assert user.verified is not True
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
        user = Users.query.filter_by(email='user@user.com').first()
        assert user.verified is not True
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
