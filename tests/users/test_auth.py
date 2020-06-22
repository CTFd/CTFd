#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from freezegun import freeze_time

from CTFd.models import Users, db
from CTFd.utils import get_config, set_config
from CTFd.utils.crypto import verify_password
from CTFd.utils.security.signing import serialize
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


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
        register_user(
            app,
            name="user1",
            email="user1@ctfd.io",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="user1",
            email="user2@ctfd.io",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="admin  ",
            email="admin2@ctfd.io",
            password="password",
            raise_for_error=False,
        )
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_register_duplicate_email():
    """A user shouldn't be able to use an already registered email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(
            app,
            name="user1",
            email="user1@ctfd.io",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="user2",
            email="user1@ctfd.io",
            password="password",
            raise_for_error=False,
        )
        user_count = Users.query.count()
        assert user_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_register_whitelisted_email():
    """A user shouldn't be able to register with an email that isn't on the whitelist"""
    app = create_ctfd()
    with app.app_context():
        set_config(
            "domain_whitelist", "whitelisted.com, whitelisted.org, whitelisted.net"
        )
        register_user(
            app, name="not_whitelisted", email="user@nope.com", raise_for_error=False
        )
        assert Users.query.count() == 1

        register_user(app, name="user1", email="user@whitelisted.com")
        assert Users.query.count() == 2

        register_user(app, name="user2", email="user@whitelisted.org")
        assert Users.query.count() == 3

        register_user(app, name="user3", email="user@whitelisted.net")
        assert Users.query.count() == 4
    destroy_ctfd(app)


def test_user_bad_login():
    """A user should not be able to login with an incorrect password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(
            app, name="user", password="wrong_password", raise_for_error=False
        )
        with client.session_transaction() as sess:
            assert sess.get("id") is None
        r = client.get("/profile")
        assert r.location.startswith(
            "http://localhost/login"
        )  # We got redirected to login
    destroy_ctfd(app)


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/profile")
        assert (
            r.location != "http://localhost/login"
        )  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_login_with_email():
    """Can a registered user can login with an email address instead of a team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user@ctfd.io", password="password")
        r = client.get("/profile")
        assert (
            r.location != "http://localhost/login"
        )  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_logout():
    """Can a registered user load /logout"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        client.get("/logout", follow_redirects=True)
        r = client.get("/challenges")
        assert r.location == "http://localhost/login?next=%2Fchallenges%3F"
        assert r.status_code == 302
    destroy_ctfd(app)


def test_user_isnt_admin():
    """A registered user cannot access admin pages"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        for page in [
            "pages",
            "users",
            "teams",
            "scoreboard",
            "challenges",
            "statistics",
            "config",
        ]:
            r = client.get("/admin/{}".format(page))
            assert r.location.startswith("http://localhost/login?next=")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_expired_confirmation_links():
    """Test that expired confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2019-02-24 03:21:34"):
        set_config("verify_emails", True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = "http://localhost/confirm/InVzZXJAdXNlci5jb20i.TxD0vg.cAGwAy8cK1T0saEEbrDEBVF2plI"
        r = client.get(confirm_link)

        assert "Your confirmation link has expired" in r.get_data(as_text=True)
        user = Users.query.filter_by(email="user@user.com").first()
        assert user.verified is not True
    destroy_ctfd(app)


def test_invalid_confirmation_links():
    """Test that invalid confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config("verify_emails", True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = "http://localhost/confirm/a8375iyu<script>alert(1)<script>hn3048wueorighkgnsfg"
        r = client.get(confirm_link)

        assert "Your confirmation token is invalid" in r.get_data(as_text=True)
        user = Users.query.filter_by(email="user@user.com").first()
        assert user.verified is not True
    destroy_ctfd(app)


def test_expired_reset_password_link():
    """Test that expired reset password links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client, freeze_time("2019-02-24 03:21:34"):
            # user@user.com "2012-01-14 03:21:34"
            forgot_link = "http://localhost/reset_password/InVzZXJAdXNlci5jb20i.TxD0vg.cAGwAy8cK1T0saEEbrDEBVF2plI"
            r = client.get(forgot_link)

            assert "Your link has expired" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_invalid_reset_password_link():
    """Test that invalid reset password links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            # user@user.com "2012-01-14 03:21:34"
            forgot_link = "http://localhost/reset_password/5678ytfghjiu876tyfg<INVALID DATA>hvbnmkoi9u87y6trdf"
            r = client.get(forgot_link)

            assert "Your reset token is invalid" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_contact_for_password_reset():
    """Test that if there is no mailserver configured, users should contact admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            forgot_link = "http://localhost/reset_password"
            r = client.get(forgot_link)

            assert "contact an organizer" in r.get_data(as_text=True)
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_user_can_confirm_email(mock_smtp):
    """Test that a user is capable of confirming their email address"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2012-01-14 03:21:34"):
        # Set CTFd to only allow confirmed users and send emails
        set_config("verify_emails", True)
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        register_user(app, name="user1", email="user@user.com")

        # Teams are not verified by default
        user = Users.query.filter_by(email="user@user.com").first()
        assert user.verified is False

        client = login_as_user(app, name="user1", password="password")

        r = client.get("http://localhost/confirm")
        assert "Need to resend the confirmation email?" in r.get_data(as_text=True)

        # smtp send message function was called
        mock_smtp.return_value.send_message.assert_called()

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce")}
            r = client.post("http://localhost/confirm", data=data)
            assert "Confirmation email sent to" in r.get_data(as_text=True)

            r = client.get("/challenges")
            assert (
                r.location == "http://localhost/confirm"
            )  # We got redirected to /confirm

            r = client.get("http://localhost/confirm/" + serialize("user@user.com"))
            assert r.location == "http://localhost/challenges"

            # The team is now verified
            user = Users.query.filter_by(email="user@user.com").first()
            assert user.verified is True

            r = client.get("http://localhost/confirm")
            assert r.location == "http://localhost/settings"
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_user_can_reset_password(mock_smtp):
    """Test that a user is capable of resetting their password"""
    from email.message import EmailMessage

    app = create_ctfd()
    with app.app_context(), freeze_time("2012-01-14 03:21:34"):
        # Set CTFd to send emails
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        # Create a user
        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            client.get("/reset_password")

            # Build reset password data
            with client.session_transaction() as sess:
                data = {"nonce": sess.get("nonce"), "email": "user@user.com"}

            # Issue the password reset request
            client.post("/reset_password", data=data)

            ctf_name = get_config("ctf_name")
            from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
            from_addr = "{} <{}>".format(ctf_name, from_addr)

            to_addr = "user@user.com"

            # Build the email
            msg = (
                "Did you initiate a password reset? If you didn't initiate this request you can ignore this email. "
                "\n\nClick the following link to reset your password:\n"
                "http://localhost/reset_password/InVzZXJAdXNlci5jb20i.TxD0vg.28dY_Gzqb1TH9nrcE_H7W8YFM-U"
            )
            ctf_name = get_config("ctf_name")

            email_msg = EmailMessage()
            email_msg.set_content(msg)

            email_msg["Subject"] = "Password Reset Request from {ctf_name}".format(
                ctf_name=ctf_name
            )
            email_msg["From"] = from_addr
            email_msg["To"] = to_addr

            # Make sure that the reset password email is sent
            mock_smtp.return_value.send_message.assert_called()
            assert str(mock_smtp.return_value.send_message.call_args[0][0]) == str(
                email_msg
            )

            # Get user's original password
            user = Users.query.filter_by(email="user@user.com").first()

            # Build the POST data
            with client.session_transaction() as sess:
                data = {"nonce": sess.get("nonce"), "password": "passwordtwo"}

            # Do the password reset
            client.get(
                "/reset_password/InVzZXJAdXNlci5jb20i.TxD0vg.28dY_Gzqb1TH9nrcE_H7W8YFM-U"
            )
            client.post(
                "/reset_password/InVzZXJAdXNlci5jb20i.TxD0vg.28dY_Gzqb1TH9nrcE_H7W8YFM-U",
                data=data,
            )

            # Make sure that the user's password changed
            user = Users.query.filter_by(email="user@user.com").first()
            assert verify_password("passwordtwo", user.password)
    destroy_ctfd(app)


def test_banned_user():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        user = Users.query.filter_by(id=2).first()
        user.banned = True
        db.session.commit()

        routes = ["/", "/challenges", "/api/v1/challenges"]
        for route in routes:
            r = client.get(route)
            assert r.status_code == 403
    destroy_ctfd(app)
