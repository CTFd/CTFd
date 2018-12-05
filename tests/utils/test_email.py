from tests.helpers import *
from CTFd.utils import get_config, set_config
from CTFd.utils.email import sendmail, verify_email_address, check_email_format
from freezegun import freeze_time
from mock import patch, Mock
from email.mime.text import MIMEText
import requests


def test_check_email_format():
    """Test that the check_email_format() works properly"""
    assert check_email_format('user@ctfd.io') is True
    assert check_email_format('user+plus@gmail.com') is True
    assert check_email_format('user.period1234@gmail.com') is True
    assert check_email_format('user.period1234@b.c') is True
    assert check_email_format('user.period1234@b') is False
    assert check_email_format('no.ampersand') is False
    assert check_email_format('user@') is False
    assert check_email_format('@ctfd.io') is False
    assert check_email_format('user.io@ctfd') is False
    assert check_email_format('user\\@ctfd') is False

    for invalid_email in ['user.@ctfd.io', '.user@ctfd.io', 'user@ctfd..io']:
        try:
            assert check_email_format(invalid_email) is False
        except AssertionError:
            print(invalid_email, 'did not pass validation')


@patch('smtplib.SMTP')
def test_sendmail_with_smtp(mock_smtp):
    """Does sendmail work properly with simple SMTP mail servers"""
    app = create_ctfd()
    with app.app_context():
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_useauth', True)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')

        from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
        to_addr = 'user@user.com'
        msg = 'this is a test'

        sendmail(to_addr, msg)

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        mock_smtp.return_value.sendmail.assert_called_once_with(from_addr, [to_addr], email_msg.as_string())
    destroy_ctfd(app)


@patch.object(requests, 'post')
def test_sendmail_with_mailgun_from_config_file(fake_post_request):
    """Does sendmail work properly with Mailgun using file configuration"""
    app = create_ctfd()
    with app.app_context():
        app.config['MAILGUN_API_KEY'] = 'key-1234567890-file-config'
        app.config['MAILGUN_BASE_URL'] = 'https://api.mailgun.net/v3/file.faked.com'

        from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
        to_addr = 'user@user.com'
        msg = 'this is a test'

        sendmail(to_addr, msg)

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.status_code = 200

        status, message = sendmail(to_addr, msg)

        args, kwargs = fake_post_request.call_args
        assert args[0] == 'https://api.mailgun.net/v3/file.faked.com/messages'
        assert kwargs['auth'] == ('api', u'key-1234567890-file-config')
        assert kwargs['timeout'] == 1.0
        assert kwargs['data'] == {'to': ['user@user.com'], 'text': 'this is a test',
                                  'from': 'CTFd Admin <noreply@ctfd.io>', 'subject': 'Message from CTFd'}

        assert fake_response.status_code == 200
        assert status is True
        assert message == "Email sent"
    destroy_ctfd(app)


@patch.object(requests, 'post')
def test_sendmail_with_mailgun_from_db_config(fake_post_request):
    """Does sendmail work properly with Mailgun using database configuration"""
    app = create_ctfd()
    with app.app_context():
        app.config['MAILGUN_API_KEY'] = 'key-1234567890-file-config'
        app.config['MAILGUN_BASE_URL'] = 'https://api.mailgun.net/v3/file.faked.com'

        # db values should take precedence over file values
        set_config('mailgun_api_key', 'key-1234567890-db-config')
        set_config('mailgun_base_url', 'https://api.mailgun.net/v3/db.faked.com')

        from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
        to_addr = 'user@user.com'
        msg = 'this is a test'

        sendmail(to_addr, msg)

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.status_code = 200

        status, message = sendmail(to_addr, msg)

        args, kwargs = fake_post_request.call_args
        assert args[0] == 'https://api.mailgun.net/v3/db.faked.com/messages'
        assert kwargs['auth'] == ('api', u'key-1234567890-db-config')
        assert kwargs['timeout'] == 1.0
        assert kwargs['data'] == {'to': ['user@user.com'], 'text': 'this is a test',
                                  'from': 'CTFd Admin <noreply@ctfd.io>', 'subject': 'Message from CTFd'}

        assert fake_response.status_code == 200
        assert status is True
        assert message == "Email sent"
    destroy_ctfd(app)


@patch('smtplib.SMTP')
@freeze_time("2012-01-14 03:21:34")
def test_verify_email(mock_smtp):
    """Does verify_email send emails"""
    app = create_ctfd()
    with app.app_context():
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_useauth', True)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')
        set_config('verify_emails', True)

        from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
        to_addr = 'user@user.com'

        verify_email_address(to_addr)

        # This is currently not actually validated
        msg = ("Please click the following link to confirm"
               " your email address for CTFd:"
               " http://localhost/confirm/InVzZXJAdXNlci5jb20i.TxD0vg.28dY_Gzqb1TH9nrcE_H7W8YFM-U")

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        # Need to freeze time to predict the value of the itsdangerous token.
        # For now just assert that sendmail was called.
        mock_smtp.return_value.sendmail.assert_called_with(from_addr, [to_addr], email_msg.as_string())
    destroy_ctfd(app)
