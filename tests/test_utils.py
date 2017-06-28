#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import ip2long, long2ip
from CTFd.utils import override_template
import json


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


def test_admin_override_template():
    """Does override_template work properly for the admin panel"""
    app = create_ctfd()
    with app.app_context():
        override_template('admin/team.html', 'ADMIN TEAM OVERRIDE')
        with app.app_context():
            client = login_as_user(app, name="admin", password="password")
            r = client.get('/admin/team/1')
            assert r.status_code == 200
            output = r.get_data(as_text=True)
            assert 'ADMIN TEAM OVERRIDE' in output
