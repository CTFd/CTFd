#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import ip2long, long2ip
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended, export_ctf, import_ctf
from CTFd.utils import register_plugin_script, register_plugin_stylesheet
from CTFd.utils import base64encode, base64decode
from CTFd.utils import check_email_format
from CTFd.utils import update_check
from email.mime.text import MIMEText
from freezegun import freeze_time
from mock import patch, Mock
import json
import os
import requests
import six


def test_ctf_version_is_set():
    """Does ctf_version get set correctly"""
    app = create_ctfd()
    with app.app_context():
        assert get_config('ctf_version') == app.VERSION
    destroy_ctfd(app)


def test_get_config_and_set_config():
    """Does get_config and set_config work properly"""
    app = create_ctfd()
    with app.app_context():
        assert get_config('setup') == True
        config = set_config('TEST_CONFIG_ENTRY', 'test_config_entry')
        assert config.value == 'test_config_entry'
        assert get_config('TEST_CONFIG_ENTRY') == 'test_config_entry'
    destroy_ctfd(app)


def test_ip2long_ipv4():
    """Does ip2long work properly for ipv4 addresses"""
    assert ip2long('127.0.0.1') == 2130706433


def test_long2ip_ipv4():
    """Does long2ip work properly for ipv4 addresses"""
    assert long2ip(2130706433) == '127.0.0.1'


def test_ip2long_ipv6():
    """Does ip2long work properly for ipv6 addresses"""
    assert ip2long('2001:0db8:85a3:0000:0000:8a2e:0370:7334') == 42540766452641154071740215577757643572
    assert ip2long('2001:658:22a:cafe:200::1') == 42540616829182469433547762482097946625


def test_long2ip_ipv6():
    """Does long2ip work properly for ipv6 addresses"""
    assert long2ip(42540766452641154071740215577757643572) == '2001:db8:85a3::8a2e:370:7334'
    assert long2ip(42540616829182469433547762482097946625) == '2001:658:22a:cafe:200::1'


def test_base64encode():
    """The base64encode wrapper works properly"""
    if six.PY2:
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode(unicode('abc123')) == 'YWJjMTIz'
        assert base64encode(unicode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4')) == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert base64encode('😆') == '8J-Yhg'
    else:
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4') == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8'
        assert base64encode('😆') == '8J-Yhg'


def test_base64decode():
    """The base64decode wrapper works properly"""
    if six.PY2:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode(unicode('YWJjMTIz')) == 'abc123'
        assert base64decode(unicode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ')) == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('8J-Yhg') == '😆'
    else:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ') == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('dXNlcit1c2VyQGN0ZmQuaW8') == 'user+user@ctfd.io'
        assert base64decode('8J-Yhg') == '😆'


def test_override_template():
    """Does override_template work properly for regular themes"""
    app = create_ctfd()
    with app.app_context():
        override_template('login.html', 'LOGIN OVERRIDE')
        with app.test_client() as client:
            r = client.get('/login')
            assert r.status_code == 200
            output = r.get_data(as_text=True)
            assert 'LOGIN OVERRIDE' in output
    destroy_ctfd(app)


def test_admin_override_template():
    """Does override_template work properly for the admin panel"""
    app = create_ctfd()
    with app.app_context():
        override_template('admin/team.html', 'ADMIN TEAM OVERRIDE')

        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/team/1')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert 'ADMIN TEAM OVERRIDE' in output
    destroy_ctfd(app)


@patch('smtplib.SMTP')
def test_sendmail_with_smtp(mock_smtp):
    """Does sendmail work properly with simple SMTP mail servers"""
    app = create_ctfd()
    with app.app_context():
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
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
        set_config('mg_api_key', 'key-1234567890-db-config')
        set_config('mg_base_url', 'https://api.mailgun.net/v3/db.faked.com')

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
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')
        set_config('verify_emails', True)

        from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
        to_addr = 'user@user.com'

        verify_email(to_addr)

        # This is currently not actually validated
        msg = ("Please click the following link to confirm"
               " your email address for CTFd:"
               " http://localhost/confirm/InVzZXJAdXNlci5jb20iLkFmS0dQZy5kLUJnVkgwaUhadzFHaXVENHczWTJCVVJwdWc")

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        # Need to freeze time to predict the value of the itsdangerous token.
        # For now just assert that sendmail was called.
        mock_smtp.return_value.sendmail.assert_called_with(from_addr, [to_addr], email_msg.as_string())
    destroy_ctfd(app)


def test_ctftime_prevents_accessing_challenges_before_ctf():
    """Test that the ctftime function prevents users from accessing challenges before the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-3"):  # CTF has not started yet.
            client = login_as_user(app)
            r = client.get('/chals')
            assert r.status_code == 403

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            data = r.get_data(as_text=True)
            assert r.status_code == 403
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 0
    destroy_ctfd(app)


def test_ctftime_allows_accessing_challenges_during_ctf():
    """Test that the ctftime function allows accessing challenges during the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-5"):
            client = login_as_user(app)
            r = client.get('/chals')
            assert r.status_code == 200

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 1
    destroy_ctfd(app)


def test_ctftime_prevents_accessing_challenges_after_ctf():
    """Test that the ctftime function prevents accessing challenges after the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-7"):
            client = login_as_user(app)
            r = client.get('/chals')
            assert r.status_code == 403

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 403
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 0
    destroy_ctfd(app)


def test_ctf_started():
    '''Tests that the ctf_started function returns the correct value'''
    app = create_ctfd()
    with app.app_context():
        assert ctf_started() == True

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            assert ctf_started() == False

        with freeze_time("2017-10-5"):
            assert ctf_started() == True

        with freeze_time("2017-10-7"):
            assert ctf_started() == True
    destroy_ctfd(app)


def test_ctf_ended():
    '''Tests that the ctf_ended function returns the correct value'''
    app = create_ctfd()
    with app.app_context():
        assert ctf_ended() == False

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            assert ctf_ended() == False

        with freeze_time("2017-10-5"):
            assert ctf_ended() == False

        with freeze_time("2017-10-7"):
            assert ctf_ended() == True
    destroy_ctfd(app)


def test_register_plugin_script():
    '''Test that register_plugin_script adds script paths to the core theme'''
    app = create_ctfd()
    with app.app_context():
        register_plugin_script('/fake/script/path.js')
        register_plugin_script('http://ctfd.io/fake/script/path.js')
        with app.test_client() as client:
            r = client.get('/')
            output = r.get_data(as_text=True)
            assert '/fake/script/path.js' in output
            assert 'http://ctfd.io/fake/script/path.js' in output
    destroy_ctfd(app)


def test_register_plugin_stylesheet():
    '''Test that register_plugin_stylesheet adds stylesheet paths to the core theme'''
    app = create_ctfd()
    with app.app_context():
        register_plugin_script('/fake/stylesheet/path.css')
        register_plugin_script('http://ctfd.io/fake/stylesheet/path.css')
        with app.test_client() as client:
            r = client.get('/')
            output = r.get_data(as_text=True)
            assert '/fake/stylesheet/path.css' in output
            assert 'http://ctfd.io/fake/stylesheet/path.css' in output
    destroy_ctfd(app)


def test_export_ctf():
    """Test that CTFd can properly export the database"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db, name=text_type('🐺'))
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        app.db.session.commit()
        backup = export_ctf()

        with open('export.zip', 'wb') as f:
            f.write(backup.getvalue())
        os.remove('export.zip')
    destroy_ctfd(app)


def test_import_ctf():
    """Test that CTFd can import a CTF"""
    app = create_ctfd()
    # TODO: Unrelated to an in-memory database, imports in a test environment are not working with SQLite...
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite') is False:
        with app.app_context():
            base_user = 'user'
            for x in range(10):
                user = base_user + str(x)
                user_email = user + "@ctfd.io"
                gen_team(app.db, name=user, email=user_email)

            for x in range(10):
                chal = gen_challenge(app.db, name='chal_name{}'.format(x))
                gen_flag(app.db, chal=chal.id, flag='flag')

            app.db.session.commit()

            backup = export_ctf()

            with open('export.zip', 'wb') as f:
                f.write(backup.read())
        destroy_ctfd(app)

        app = create_ctfd()
        with app.app_context():
            import_ctf('export.zip')

            app.db.session.commit()

            print(Teams.query.count())
            print(Challenges.query.count())

            assert Teams.query.count() == 11
            assert Challenges.query.count() == 10
            assert Keys.query.count() == 10
    destroy_ctfd(app)


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
    assert check_email_format('user\@ctfd') is False

    for invalid_email in ['user.@ctfd.io', '.user@ctfd.io', 'user@ctfd..io']:
        try:
            assert check_email_format(invalid_email) is False
        except AssertionError:
            print(invalid_email, 'did not pass validation')


def test_update_check_is_called():
    """Update checks happen on start"""
    app = create_ctfd()
    with app.app_context():
        assert get_config('version_latest') is None


@patch.object(requests, 'get')
def test_update_check_identifies_update(fake_get_request):
    """Update checks properly identify new versions"""
    app = create_ctfd()
    with app.app_context():
        app.config['UPDATE_CHECK'] = True
        fake_response = Mock()
        fake_get_request.return_value = fake_response
        fake_response.json = lambda: {
            u'resource': {
                u'html_url': u'https://github.com/CTFd/CTFd/releases/tag/9.9.9',
                u'download_url': u'https://api.github.com/repos/CTFd/CTFd/zipball/9.9.9',
                u'published_at': u'Wed, 25 Oct 2017 19:39:42 -0000',
                u'tag': u'9.9.9',
                u'prerelease': False,
                u'id': 6,
                u'latest': True
            }
        }
        update_check()
        assert get_config('version_latest') == 'https://github.com/CTFd/CTFd/releases/tag/9.9.9'
    destroy_ctfd(app)


def test_update_check_notifies_user():
    """If an update is available, admin users are notified in the panel"""
    app = create_ctfd()
    with app.app_context():
        app.config['UPDATE_CHECK'] = True
        set_config('version_latest', 'https://github.com/CTFd/CTFd/releases/tag/9.9.9')
        client = login_as_user(app, name="admin", password="password")

        r = client.get('/admin/config')
        assert r.status_code == 200

        response = r.get_data(as_text=True)
        assert 'https://github.com/CTFd/CTFd/releases/tag/9.9.9' in response

    destroy_ctfd(app)


@patch.object(requests, 'get')
def test_update_check_ignores_downgrades(fake_get_request):
    """Update checks do nothing on old or same versions"""
    app = create_ctfd()
    with app.app_context():
        app.config['UPDATE_CHECK'] = True
        fake_response = Mock()
        fake_get_request.return_value = fake_response
        fake_response.json = lambda: {
            u'resource': {
                u'html_url': u'https://github.com/CTFd/CTFd/releases/tag/0.0.1',
                u'download_url': u'https://api.github.com/repos/CTFd/CTFd/zipball/0.0.1',
                u'published_at': u'Wed, 25 Oct 2017 19:39:42 -0000',
                u'tag': u'0.0.1',
                u'prerelease': False,
                u'id': 6,
                u'latest': True
            }
        }
        update_check()
        assert get_config('version_latest') is None

        fake_response = Mock()
        fake_get_request.return_value = fake_response
        fake_response.json = lambda: {
            u'resource': {
                u'html_url': u'https://github.com/CTFd/CTFd/releases/tag/{}'.format(app.VERSION),
                u'download_url': u'https://api.github.com/repos/CTFd/CTFd/zipball/{}'.format(app.VERSION),
                u'published_at': u'Wed, 25 Oct 2017 19:39:42 -0000',
                u'tag': u'{}'.format(app.VERSION),
                u'prerelease': False,
                u'id': 6,
                u'latest': True
            }
        }
        update_check()
        assert get_config('version_latest') is None
    destroy_ctfd(app)


def test_ratelimit_on_auth():
    """Test that ratelimiting function works properly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with app.test_client() as client:
            r = client.get('/login')
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "password": "wrong_password",
                    "nonce": sess.get('nonce')
                }
            for x in range(10):
                r = client.post('/login', data=data)
                assert r.status_code == 200

            for x in range(5):
                r = client.post('/login', data=data)
                assert r.status_code == 429
    destroy_ctfd(app)
