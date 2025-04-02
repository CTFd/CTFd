from email.message import EmailMessage
from unittest.mock import Mock, patch

import requests

from CTFd.models import Users
from CTFd.utils import get_config, set_config
from CTFd.utils.crypto import verify_password
from CTFd.utils.email import (
    check_email_is_blacklisted,
    check_email_is_whitelisted,
    forgot_password,
    sendmail,
    successful_registration_notification,
    verify_email_address,
)
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


@patch("smtplib.SMTP")
def test_sendmail_with_smtp_from_config_file(mock_smtp):
    """Does sendmail work properly with simple SMTP mail servers using file configuration"""
    app = create_ctfd()
    with app.app_context():
        app.config["MAIL_SERVER"] = "localhost"
        app.config["MAIL_PORT"] = "25"
        app.config["MAIL_USEAUTH"] = "True"
        app.config["MAIL_USERNAME"] = "username"
        app.config["MAIL_PASSWORD"] = "password"

        ctf_name = get_config("ctf_name")
        from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
        from_addr = "{} <{}>".format(ctf_name, from_addr)

        to_addr = "user@user.com"
        msg = "this is a test"

        sendmail(to_addr, msg)

        ctf_name = get_config("ctf_name")

        email_msg = EmailMessage()
        email_msg.set_content(msg)

        email_msg["Subject"] = "Message from {0}".format(ctf_name)
        email_msg["From"] = from_addr
        email_msg["To"] = to_addr

        mock_smtp.return_value.send_message.assert_called()
        assert str(mock_smtp.return_value.send_message.call_args[0][0]) == str(
            email_msg
        )
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_sendmail_with_smtp_from_db_config(mock_smtp):
    """Does sendmail work properly with simple SMTP mail servers using database configuration"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        ctf_name = get_config("ctf_name")
        from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
        from_addr = "{} <{}>".format(ctf_name, from_addr)

        to_addr = "user@user.com"
        msg = "this is a test"

        sendmail(to_addr, msg)

        ctf_name = get_config("ctf_name")
        email_msg = EmailMessage()
        email_msg.set_content(msg)
        email_msg["Subject"] = "Message from {0}".format(ctf_name)
        email_msg["From"] = from_addr
        email_msg["To"] = to_addr

        mock_smtp.return_value.send_message.assert_called()
        assert str(mock_smtp.return_value.send_message.call_args[0][0]) == str(
            email_msg
        )
    destroy_ctfd(app)


@patch.object(requests, "post")
def test_sendmail_with_mailgun_from_config_file(fake_post_request):
    """Does sendmail work properly with Mailgun using file configuration"""
    app = create_ctfd()
    with app.app_context():
        app.config["MAILGUN_API_KEY"] = "key-1234567890-file-config"
        app.config["MAILGUN_BASE_URL"] = "https://api.mailgun.net/v3/file.faked.com"

        to_addr = "user@user.com"
        msg = "this is a test"

        sendmail(to_addr, msg)

        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.status_code = 200

        status, message = sendmail(to_addr, msg)

        args, kwargs = fake_post_request.call_args
        assert args[0] == "https://api.mailgun.net/v3/file.faked.com/messages"
        assert kwargs["auth"] == ("api", "key-1234567890-file-config")
        assert kwargs["timeout"] == 1.0
        assert kwargs["data"] == {
            "to": ["user@user.com"],
            "text": "this is a test",
            "from": "CTFd <noreply@examplectf.com>",
            "subject": "Message from CTFd",
        }

        assert fake_response.status_code == 200
        assert status is True
        assert message == "Email sent"
    destroy_ctfd(app)


@patch.object(requests, "post")
def test_sendmail_with_mailgun_from_db_config(fake_post_request):
    """Does sendmail work properly with Mailgun using database configuration"""
    app = create_ctfd()
    with app.app_context():
        app.config["MAILGUN_API_KEY"] = "key-1234567890-file-config"
        app.config["MAILGUN_BASE_URL"] = "https://api.mailgun.net/v3/file.faked.com"

        # db values should take precedence over file values
        set_config("mailgun_api_key", "key-1234567890-db-config")
        set_config("mailgun_base_url", "https://api.mailgun.net/v3/db.faked.com")

        to_addr = "user@user.com"
        msg = "this is a test"

        sendmail(to_addr, msg)

        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.status_code = 200

        status, message = sendmail(to_addr, msg)

        args, kwargs = fake_post_request.call_args
        assert args[0] == "https://api.mailgun.net/v3/db.faked.com/messages"
        assert kwargs["auth"] == ("api", "key-1234567890-db-config")
        assert kwargs["timeout"] == 1.0
        assert kwargs["data"] == {
            "to": ["user@user.com"],
            "text": "this is a test",
            "from": "CTFd <noreply@examplectf.com>",
            "subject": "Message from CTFd",
        }

        assert fake_response.status_code == 200
        assert status is True
        assert message == "Email sent"
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_verify_email(mock_smtp):
    """Does verify_email send emails"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)

        ctf_name = get_config("ctf_name")
        from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
        from_addr = "{} <{}>".format(ctf_name, from_addr)

        to_addr = "user@user.com"

        urandom_value = b"\xff" * 32
        with patch("os.urandom", return_value=urandom_value):
            verify_email_address(to_addr)

        msg = (
            "Welcome to CTFd!\n\n"
            "Click the following link to confirm and activate your account:\n"
            "http://localhost/confirm/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\n\n"
            "If the link is not clickable, try copying and pasting it into your browser."
        )

        ctf_name = get_config("ctf_name")
        email_msg = EmailMessage()
        email_msg.set_content(msg)
        email_msg["Subject"] = "Confirm your account for {ctf_name}".format(
            ctf_name=ctf_name
        )
        email_msg["From"] = from_addr
        email_msg["To"] = to_addr

        mock_smtp.return_value.send_message.assert_called()
        assert str(mock_smtp.return_value.send_message.call_args[0][0]) == str(
            email_msg
        )
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_successful_registration_email(mock_smtp):
    """Does successful_registration_notification send emails"""
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)

        ctf_name = get_config("ctf_name")
        from_addr = get_config("mailfrom_addr") or app.config.get("MAILFROM_ADDR")
        from_addr = "{} <{}>".format(ctf_name, from_addr)

        to_addr = "user@user.com"

        successful_registration_notification(to_addr)

        msg = "You've successfully registered for CTFd!"

        email_msg = EmailMessage()
        email_msg.set_content(msg)
        email_msg["Subject"] = "Successfully registered for {ctf_name}".format(
            ctf_name=ctf_name
        )
        email_msg["From"] = from_addr
        email_msg["To"] = to_addr

        mock_smtp.return_value.send_message.assert_called()
        assert str(mock_smtp.return_value.send_message.call_args[0][0]) == str(
            email_msg
        )
    destroy_ctfd(app)


def test_email_whitelist():
    app = create_ctfd()
    with app.app_context():
        set_config("domain_whitelist", "example.com")
        test_cases_specific_domain = [
            ("john.doe@example.com", True),
            ("john.doe@ext.example.com", False),
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
        ]

        for case in test_cases_specific_domain:
            email, expected = case
            assert check_email_is_whitelisted(email) is expected

        set_config("domain_whitelist", "*.example.com")
        test_cases_wildcard_domain = [
            ("john.doe@ext.example.com", True),
            ("john.doe@.example.com", True),  # this is expected behaviour
            ("john.doe@example.com", False),
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
            ("john.doe@*example.com", False),
            ("john.doe@*.example.com", False),
        ]

        for case in test_cases_wildcard_domain:
            email, expected = case
            assert check_email_is_whitelisted(email) is expected

        set_config("domain_whitelist", "example.com, *.example.com")
        test_cases_combined_domain = [
            ("john.doe@example.com", True),
            ("john.doe@ext.example.com", True),
            ("john.doe@.example.com", True),  # this is expected behaviour
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@gmail.com", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
            ("john.doe@*example.com", False),
            ("john.doe@*.example.com", False),
        ]

        for case in test_cases_combined_domain:
            email, expected = case
            assert check_email_is_whitelisted(email) is expected

        set_config("domain_whitelist", "example.com, uni.acme.com, *.edu, *.edu.de")

        test_cases_multiple_combined_domains = [
            ("john.doe@example.com", True),
            ("john.doe@uni.acme.com", True),
            ("john.doe@uni.edu", True),
            ("john.doe@cs.uni.edu", True),
            ("john.doe@mail.cs.uni.edu", True),
            ("john.doe@uni.edu.de", True),
            ("john.doe@cs.uni.edu.de", True),
            ("john.doe@mail.cs.uni.edu.de", True),
            ("john.doe@gmail.com", False),
            ("john.doe@ample.com", False),
            ("john.doe@example1.com", False),
            ("john.doe@1example.com", False),
            ("john.doe@ext.example.com", False),
            ("john.doe@cs.acme.com", False),
            ("john.doe@edu.com", False),
            ("john.doe@mail.uni.acme.com", False),
            ("john.doe@edu", False),
        ]

        for case in test_cases_multiple_combined_domains:
            email, expected = case
            assert check_email_is_whitelisted(email) is expected
    destroy_ctfd(app)


def test_email_blacklist():
    app = create_ctfd()
    with app.app_context():
        set_config("domain_blacklist", "example.com")
        test_cases_specific_domain = [
            ("john.doe@example.com", True),
            ("john.doe@ext.example.com", False),
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
        ]

        for case in test_cases_specific_domain:
            email, expected = case
            assert check_email_is_blacklisted(email) is expected

        set_config("domain_blacklist", "*.example.com")
        test_cases_wildcard_domain = [
            ("john.doe@ext.example.com", True),
            ("john.doe@.example.com", True),
            ("john.doe@example.com", False),
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
            ("john.doe@*example.com", True),
            ("john.doe@*.example.com", True),
        ]

        for case in test_cases_wildcard_domain:
            email, expected = case
            assert check_email_is_blacklisted(email) is expected

        set_config("domain_blacklist", "example.com, *.example.com")
        test_cases_combined_domain = [
            ("john.doe@example.com", True),
            ("john.doe@ext.example.com", True),
            ("john.doe@.example.com", True),
            ("john.doe@example.io", False),
            ("john.doe@example.co", False),
            ("john.doe@gmail.com", False),
            ("john.doe@ample.com", False),
            ("john.doe@exexample.com", False),
            ("john.doe@*example.com", True),
            ("john.doe@*.example.com", True),
        ]

        for case in test_cases_combined_domain:
            email, expected = case
            assert check_email_is_blacklisted(email) is expected

        set_config("domain_blacklist", "example.com, uni.acme.com, *.edu, *.edu.de")
        test_cases_multiple_combined_domains = [
            ("john.doe@example.com", True),
            ("john.doe@uni.acme.com", True),
            ("john.doe@uni.edu", True),
            ("john.doe@cs.uni.edu", True),
            ("john.doe@mail.cs.uni.edu", True),
            ("john.doe@uni.edu.de", True),
            ("john.doe@cs.uni.edu.de", True),
            ("john.doe@mail.cs.uni.edu.de", True),
            ("john.doe@gmail.com", False),
            ("john.doe@ample.com", False),
            ("john.doe@example1.com", False),
            ("john.doe@1example.com", False),
            ("john.doe@ext.example.com", False),
            ("john.doe@cs.acme.com", False),
            ("john.doe@edu.com", False),
            ("john.doe@mail.uni.acme.com", False),
            ("john.doe@edu", False),
        ]

        for case in test_cases_multiple_combined_domains:
            email, expected = case
            assert check_email_is_blacklisted(email) is expected
    destroy_ctfd(app)


def test_confirm_links_single_use():
    """Test that confirm links are single use"""
    app = create_ctfd()
    with app.app_context():
        set_config("verify_emails", True)
        register_user(app)
        client = login_as_user(app)

        to_addr = "user@examplectf.com"

        urandom_value = b"\xff" * 32
        with patch("os.urandom", return_value=urandom_value):
            verify_email_address(to_addr)

        r = client.get(
            "http://localhost/confirm/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
        user = Users.query.filter_by(email=to_addr).first()
        assert user.verified is True

        r = client.get(
            "http://localhost/confirm/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
        assert (
            "Your confirmation link is invalid, please generate a new one"
            in r.get_data(as_text=True)
        )
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_confirm_link_tokens_unique(mock_smtp):
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        verify_email_address("user1@examplectf.com")
        call1 = str(mock_smtp.return_value.send_message.call_args[0][0])

        verify_email_address("user1@examplectf.com")
        call2 = str(mock_smtp.return_value.send_message.call_args[0][0])

        verify_email_address("user2@examplectf.com")
        call3 = str(mock_smtp.return_value.send_message.call_args[0][0])
        assert call1 != call2
        assert call2 != call3
        assert call1 != call3
    destroy_ctfd(app)


def test_reset_password_links_single_use():
    """Test that reset password links are single use"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        with app.test_client() as client:
            client.get("/reset_password")

            # Build reset password data
            with client.session_transaction() as sess:
                data = {"nonce": sess.get("nonce"), "email": "user@examplectf.com"}

            # Issue the password reset request
            urandom_value = b"\xff" * 32
            with patch("os.urandom", return_value=urandom_value):
                client.post("/reset_password", data=data)

            # Get user's original password
            user = Users.query.filter_by(email="user@examplectf.com").first()

            # Build the POST data
            with client.session_transaction() as sess:
                data = {"nonce": sess.get("nonce"), "password": "passwordtwo"}

            # Do the password reset
            r = client.get(
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            )
            assert r.status_code == 200
            r = client.post(
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                data=data,
            )
            assert r.status_code == 302

            # Make sure that the user's password changed
            user = Users.query.filter_by(email="user@examplectf.com").first()
            assert verify_password("passwordtwo", user.password)

            # Attempt to re-use the password reset link
            r = client.get(
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
            )
            assert (
                "Your reset link is invalid, please generate a new one"
                in r.get_data(as_text=True)
            )
            assert r.status_code == 200
            with client.session_transaction() as sess:
                data = {"nonce": sess.get("nonce"), "password": "passwordthree"}
            r = client.post(
                "/reset_password/ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                data=data,
            )
            assert r.status_code == 200
            # Password should not have been changed
            user = Users.query.filter_by(email="user@examplectf.com").first()
            assert verify_password("passwordthree", user.password) is False
    destroy_ctfd(app)


@patch("smtplib.SMTP")
def test_reset_password_link_tokens_unique(mock_smtp):
    app = create_ctfd()
    with app.app_context():
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")
        set_config("verify_emails", True)
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        forgot_password("user1@examplectf.com")
        call1 = str(mock_smtp.return_value.send_message.call_args[0][0])

        forgot_password("user1@examplectf.com")
        call2 = str(mock_smtp.return_value.send_message.call_args[0][0])

        forgot_password("user2@examplectf.com")
        call3 = str(mock_smtp.return_value.send_message.call_args[0][0])
        assert call1 != call2
        assert call2 != call3
        assert call1 != call3
    destroy_ctfd(app)
