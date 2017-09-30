#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import ip2long, long2ip
from CTFd.plugins import register_plugin_assets_directory, register_plugin_asset
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
