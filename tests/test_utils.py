#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import ip2long, long2ip
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email
from CTFd.utils import base64encode, base64decode
from freezegun import freeze_time
from mock import patch
import json
import six


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
        assert base64encode(unicode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'), urlencode=True) == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ%3D'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8='
        assert base64encode('user+user@ctfd.io', urlencode=True) == 'dXNlcit1c2VyQGN0ZmQuaW8%3D'
        assert base64encode('😆') == '8J-Yhg=='
        assert base64encode('😆', urlencode=True) == '8J-Yhg%3D%3D'
    else:
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode('abc123') == 'YWJjMTIz'
        assert base64encode('"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4', urlencode=True) == 'InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ%3D'
        assert base64encode('user+user@ctfd.io') == 'dXNlcit1c2VyQGN0ZmQuaW8='
        assert base64encode('user+user@ctfd.io', urlencode=True) == 'dXNlcit1c2VyQGN0ZmQuaW8%3D'
        assert base64encode('😆') == '8J-Yhg=='
        assert base64encode('😆', urlencode=True) == '8J-Yhg%3D%3D'


def test_base64decode():
    """The base64decode wrapper works properly"""
    if six.PY2:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode(unicode('YWJjMTIz')) == 'abc123'
        assert base64decode(unicode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ%3D'), urldecode=True) == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('8J-Yhg==') == '😆'
        assert base64decode('8J-Yhg%3D%3D', urldecode=True) == '😆'
    else:
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode('YWJjMTIz') == 'abc123'
        assert base64decode('InRlc3RAbWFpbGluYXRvci5jb20iLkRHeGVvQS5sQ3NzVTNNMlF1QmZvaE8tRnRkZ0RRTEtiVTQ%3D', urldecode=True) == '"test@mailinator.com".DGxeoA.lCssU3M2QuBfohO-FtdgDQLKbU4'
        assert base64decode('dXNlcit1c2VyQGN0ZmQuaW8=') == 'user+user@ctfd.io'
        assert base64decode('dXNlcit1c2VyQGN0ZmQuaW8%3D', urldecode=True) == 'user+user@ctfd.io'
        assert base64decode('8J-Yhg==') == '😆'
        assert base64decode('8J-Yhg%3D%3D', urldecode=True) == '😆'


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
    from email.mime.text import MIMEText
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


@patch('smtplib.SMTP')
@freeze_time("2012-01-14 03:21:34")
def test_verify_email(mock_smtp):
    """Does verify_email send emails"""
    from email.mime.text import MIMEText
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
               " http://localhost/confirm/InVzZXJAdXNlci5jb20iLkFmS0dQZy5kLUJnVkgwaUhadzFHaXVENHczWTJCVVJwdWc%3D")

        ctf_name = get_config('ctf_name')
        email_msg = MIMEText(msg)
        email_msg['Subject'] = "Message from {0}".format(ctf_name)
        email_msg['From'] = from_addr
        email_msg['To'] = to_addr

        # Need to freeze time to predict the value of the itsdangerous token.
        # For now just assert that sendmail was called.
        mock_smtp.return_value.sendmail.assert_called_with(from_addr, [to_addr], email_msg.as_string())
    destroy_ctfd(app)
