#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import ip2long, long2ip
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_plugin_asset,
    register_plugin_script,
    register_plugin_stylesheet,
    override_template
)
from freezegun import freeze_time
from mock import patch
import json
import six


def test_register_plugin_asset():
    """Test that plugin asset registration works"""
    app = create_ctfd(setup=False)
    register_plugin_asset(app, asset_path='/plugins/__init__.py')
    app = setup_ctfd(app)
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/plugins/__init__.py')
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
    destroy_ctfd(app)


def test_register_plugin_assets_directory():
    """Test that plugin asset directory registration works"""
    app = create_ctfd(setup=False)
    register_plugin_assets_directory(app, base_path='/plugins/')
    app = setup_ctfd(app)
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/plugins/__init__.py')
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
            r = client.get('/plugins/challenges/__init__.py')
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
    destroy_ctfd(app)


def test_override_template():
    """Does override_template work properly for regular themes when used from a plugin"""
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
    """Does override_template work properly for the admin panel when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        override_template('admin/team.html', 'ADMIN TEAM OVERRIDE')

        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/team/1')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert 'ADMIN TEAM OVERRIDE' in output
    destroy_ctfd(app)


def test_register_plugin_script():
    '''Test that register_plugin_script adds script paths to the original theme when used from a plugin'''
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
    '''Test that register_plugin_stylesheet adds stylesheet paths to the original theme when used from a plugin'''
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
