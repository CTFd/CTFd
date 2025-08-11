#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from freezegun import freeze_time

from CTFd.models import Users, db
from CTFd.utils import get_config, set_config
from CTFd.utils.crypto import verify_password
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
            email="user1@examplectf.com",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="user1",
            email="user2@examplectf.com",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="admin  ",
            email="admin2@examplectf.com",
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
            email="user1@examplectf.com",
            password="password",
            raise_for_error=False,
        )
        register_user(
            app,
            name="user2",
            email="user1@examplectf.com",
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


def test_register_blacklisted_email():
    """A user shouldn't be able to register with an email that is on the blacklist"""
    app = create_ctfd()
    with app.app_context():
        set_config(
            "domain_blacklist", "blacklisted.com, blacklisted.org, blacklisted.net"
        )
        register_user(
            app, name="blacklisted", email="user@blacklisted.com", raise_for_error=False
        )
        assert Users.query.count() == 1

        register_user(app, name="user1", email="user@yep.com")
        assert Users.query.count() == 2

        register_user(app, name="user2", email="user@yay.org")
        assert Users.query.count() == 3

        register_user(app, name="user3", email="user@yipee.net")
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
        assert r.location.startswith("/login")  # We got redirected to login
    destroy_ctfd(app)


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/profile")
        assert r.location is None  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_login_with_email():
    """Can a registered user can login with an email address instead of a team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user@examplectf.com", password="password")
        r = client.get("/profile")
        assert r.location is None  # We didn't get redirected to login
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
        assert r.location == "/login?next=%2Fchallenges%3F"
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
            assert r.location.startswith("/login?next=")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_expired_confirmation_links():
    """Test that expired confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = (
            "http://localhost/confirm/bb8a8526146e50778b211ae63074595880edbc0b"
        )
        r = client.get(confirm_link)

        assert (
            "Your confirmation link is invalid, please generate a new one"
            in r.get_data(as_text=True)
        )
        user = Users.query.filter_by(email="user@user.com").first()
        assert user.verified is not True
    destroy_ctfd(app)


def test_invalid_confirmation_links():
    """Test that invalid confirmation links are reported to the user"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)

        register_user(app, email="user@user.com")
        client = login_as_user(app, name="user", password="password")

        # user@user.com "2012-01-14 03:21:34"
        confirm_link = "http://localhost/confirm/a8375iyu<script>alert(1)<script>hn3048wueorighkgnsfg"
        r = client.get(confirm_link)

        assert (
            "Your confirmation link is invalid, please generate a new one"
            in r.get_data(as_text=True)
        )
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

        with app.test_client() as client:
            forgot_link = "http://localhost/reset_password/bb8a8526146e50778b211ae63074595880edbc0b"
            r = client.get(forgot_link)

            assert (
                "Your reset link is invalid, please generate a new one"
                in r.get_data(as_text=True)
            )
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

            assert (
                "Your reset link is invalid, please generate a new one"
                in r.get_data(as_text=True)
            )
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

        r = client.get("/confirm")
        assert "We've sent a confirmation email" in r.get_data(as_text=True)

        # smtp send message function was called
        mock_smtp.return_value.send_message.assert_called()

        with client.session_transaction() as sess:
            urandom_value = b"\xff" * 32
            with patch("os.urandom", return_value=urandom_value):
                data = {"nonce": sess.get("nonce")}
                r = client.post("http://localhost/confirm", data=data)
            assert "Confirmation email sent to" in r.get_data(as_text=True)

            r = client.get("/challenges")
            assert r.location == "/confirm"  # We got redirected to /confirm

            r = client.get(
                "http://localhost/confirm/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            )
            assert r.location == "/challenges"

            # The team is now verified
            user = Users.query.filter_by(email="user@user.com").first()
            assert user.verified is True

            r = client.get("http://localhost/confirm")
            assert r.location == "/settings"
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_user_can_reset_password(mock_smtp):
    """Test that a user is capable of resetting their password"""
    from email.message import EmailMessage

    app = create_ctfd()
    with app.app_context():
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
            urandom_value = b"\xff" * 32
            with patch("os.urandom", return_value=urandom_value):
                client.post("/reset_password", data=data)

            ctf_name = get_config("ctf_name")
            from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
            from_addr = "{} <{}>".format(ctf_name, from_addr)

            to_addr = "user@user.com"

            # Build the email
            msg = (
                "Did you initiate a password reset on CTFd? If you didn't initiate this request you can ignore this email. "
                "\n\nClick the following link to reset your password:\n"
                "http://localhost/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\n\n"
                "If the link is not clickable, try copying and pasting it into your browser."
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
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            )
            client.post(
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
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


def test_registration_code_required():
    """
    Test that registration code configuration properly blocks logins
    with missing and incorrect registration codes
    """
    app = create_ctfd()
    with app.app_context():
        # Set a registration code
        set_config("registration_code", "secret-sauce")

        with app.test_client() as client:
            # Load CSRF nonce
            r = client.get("/register")
            resp = r.get_data(as_text=True)
            assert "Registration Code" in resp
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user1@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            # Attempt registration without password
            r = client.post("/register", data=data)
            resp = r.get_data(as_text=True)
            assert "The registration code you entered was incorrect" in resp

            # Attempt registration with wrong password
            data["registration_code"] = "wrong-sauce"
            r = client.post("/register", data=data)
            resp = r.get_data(as_text=True)
            assert "The registration code you entered was incorrect" in resp

            # Attempt registration with right password
            data["registration_code"] = "secret-sauce"
            r = client.post("/register", data=data)
            assert r.status_code == 302
            assert r.location.startswith("/challenges")
    destroy_ctfd(app)


def test_registration_code_allows_numeric():
    """
    Test that registration code is allowed to be all numeric
    """
    app = create_ctfd()
    with app.app_context():
        # Set a registration code
        set_config("registration_code", "1234567890")

        with app.test_client() as client:
            # Load CSRF nonce
            r = client.get("/register")
            resp = r.get_data(as_text=True)
            assert "Registration Code" in resp
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user1@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }

            # Attempt registration with numeric registration code
            data["registration_code"] = "1234567890"
            r = client.post("/register", data=data)
            assert r.status_code == 302
            assert r.location.startswith("/challenges")
    destroy_ctfd(app)


def test_registration_password_minimum_length():
    """
    Test that registration enforces minimum password length when configured
    """
    app = create_ctfd()
    with app.app_context():
        # Set a minimum password length
        set_config("password_min_length", 8)

        with app.test_client() as client:
            # Load CSRF nonce
            r = client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user1@examplectf.com",
                    "password": "short",  # Only 5 characters
                    "nonce": sess.get("nonce"),
                }

            # Attempt registration with password too short
            r = client.post("/register", data=data)
            resp = r.get_data(as_text=True)
            assert "Password must be at least 8 characters" in resp
            assert r.status_code == 200  # Should stay on registration page

            # Verify user was not created
            user_count = Users.query.count()
            assert user_count == 1  # Only admin user exists

            # Attempt registration with password meeting minimum length
            data["password"] = "validpassword"  # 13 characters, meets minimum
            r = client.post("/register", data=data)
            assert r.status_code == 302
            assert r.location.startswith("/challenges")

            # Verify user was created
            user_count = Users.query.count()
            assert user_count == 2  # Admin user + new user

        # Test with minimum length set to 0 (disabled)
        set_config("password_min_length", 0)

        with app.test_client() as client:
            # Load CSRF nonce
            r = client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": "user2",
                    "email": "user2@examplectf.com",
                    "password": "x",  # Only 1 character
                    "nonce": sess.get("nonce"),
                }

            # Should allow short password when minimum length is 0
            r = client.post("/register", data=data)
            assert r.status_code == 302
            assert r.location.startswith("/challenges")

            # Verify user was created
            user_count = Users.query.count()
            assert user_count == 3  # Admin user + 2 new users
    destroy_ctfd(app)


def test_user_change_password_required():
    """
    Test that users with change_password=True are redirected to reset password
    and cannot access other pages until they change their password
    """
    app = create_ctfd()
    with app.app_context():
        # Create a user with change_password=True
        register_user(
            app, name="testuser", email="test@example.com", password="oldpassword"
        )
        user = Users.query.filter_by(name="testuser").first()
        user.change_password = True
        db.session.commit()

        with app.test_client() as client:
            # Login as the user
            with client.session_transaction() as sess:
                data = {
                    "name": "testuser",
                    "password": "oldpassword",
                    "nonce": sess.get("nonce"),
                }

            # Get login page first to get nonce
            client.get("/login")
            with client.session_transaction() as sess:
                data["nonce"] = sess.get("nonce")

            # Login
            r = client.post("/login", data=data)
            assert r.status_code == 302

            # Test that user is redirected to reset_password when accessing various pages
            protected_routes = [
                "/",
                "/challenges",
                "/scoreboard",
                "/profile",
                "/settings",
                "/api/v1/challenges",
            ]

            for route in protected_routes:
                r = client.get(route, follow_redirects=False)
                # Should be redirected to reset_password with a token
                assert r.status_code == 302
                assert "/reset_password/" in r.location

            # Test that the user can access the reset_password page directly
            r = client.get(route, follow_redirects=True)
            # Should end up on reset_password page
            final_url = r.request.path
            assert "/reset_password/" in final_url

            # Get redirected to reset password page with token
            r = client.get("/challenges", follow_redirects=False)
            assert r.status_code == 302
            assert "/reset_password/" in r.location

            # Extract the token from the redirect URL
            reset_url = r.location
            token = reset_url.split("/reset_password/")[-1]

            # Access the reset password page with the token
            r = client.get(f"/reset_password/{token}")
            assert r.status_code == 200

            # Actually reset the password using the reset password form
            with client.session_transaction() as sess:
                reset_data = {"password": "newpassword123", "nonce": sess.get("nonce")}

            # Submit the password reset form
            r = client.post(f"/reset_password/{token}", data=reset_data)
            assert r.status_code == 302  # Should redirect after successful reset

            # Verify the password was actually changed and change_password flag was cleared
            user = Users.query.filter_by(name="testuser").first()
            assert user.change_password is False
            assert verify_password("newpassword123", user.password)

            client.get("/login")
            with client.session_transaction() as sess:
                data = {
                    "name": "testuser",
                    "password": "newpassword123",
                    "nonce": sess.get("nonce"),
                }

            r = client.post("/login", data=data)
            assert r.status_code == 302

            # Now user should be able to access protected routes normally
            r = client.get("/challenges")
            assert r.status_code == 200
            assert r.location is None  # No redirect

            r = client.get("/profile")
            assert r.status_code == 200
            assert r.location is None  # No redirect

    destroy_ctfd(app)


def test_admin_can_set_change_password_via_api():
    """
    Test that admins can set the change_password attribute via the API
    """
    app = create_ctfd()
    with app.app_context():
        # Login as admin
        client = login_as_user(app, name="admin", password="password")

        # Create a user via API with change_password=True
        r = client.post(
            "/api/v1/users",
            json={
                "name": "apiuser",
                "email": "apiuser@example.com",
                "password": "password123",
                "change_password": True,
            },
        )
        assert r.status_code == 200

        # Verify the user was created with change_password=True
        response_data = r.get_json()
        assert response_data["success"] is True
        user_id = response_data["data"]["id"]

        user = Users.query.filter_by(id=user_id).first()
        assert user is not None
        assert user.change_password is True

        # Update user via API to set change_password=False
        r = client.patch(f"/api/v1/users/{user_id}", json={"change_password": False})
        assert r.status_code == 200

        # Verify the change_password was updated
        user = Users.query.filter_by(id=user_id).first()
        assert user.change_password is False

        # Test that non-admin users cannot set change_password via API
        register_user(app, name="normaluser", email="normal@example.com")
        normal_client = login_as_user(app, name="normaluser", password="password")

        # Try to modify change_password on their own account (should fail)
        normal_user = Users.query.filter_by(name="normaluser").first()
        r = normal_client.patch(
            f"/api/v1/users/{normal_user.id}",
            json={
                "change_password": True,
            },
        )
        # Normal users shouldn't be able to modify change_password field
        assert r.status_code == 403  # Forbidden

        # Verify that change_password was not modified
        normal_user = Users.query.filter_by(name="normaluser").first()
        assert normal_user.change_password is False

        # Also test via the /me endpoint
        r = normal_client.patch(
            "/api/v1/users/me",
            json={
                "change_password": True,
            },
        )
        # Request goes through but doesn't actually modify the attribute
        assert r.status_code == 200

        # Verify that change_password was still not modified
        normal_user = Users.query.filter_by(name="normaluser").first()
        assert normal_user.change_password is False

    destroy_ctfd(app)
