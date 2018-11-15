#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.admin import admin
from CTFd.utils import set_config, get_config
from freezegun import freeze_time
from tests.helpers import *
from mock import patch
from flask import Flask


def get_bp_urls(blueprint):
    temp_app = Flask(__name__)
    temp_app.register_blueprint(blueprint)
    return [str(p) for p in temp_app.url_map.iter_rules()]


def test_admin_access():
    """Can a user access admin pages?"""
    app = create_ctfd()
    with app.app_context():
        routes = [
            '/admin/challenges/new',
            '/admin/export/csv',
            # '/admin/pages/preview',
            '/admin/pages/new',
            '/admin/teams/new',
            '/admin/users/new',
            '/admin/notifications',
            '/admin/challenges',
            '/admin/scoreboard',
            '/admin/statistics',
            '/admin/export',
            '/admin/config',
            '/admin/pages',
            '/admin/teams',
            '/admin/users',
            '/admin',
            '/admin/submissions/correct',
            '/admin/submissions/incorrect',
            '/admin/submissions',
            '/admin/challenges/1',
            # '/admin/plugins/<plugin>',
            # '/admin/pages/<int:page_id>',
            '/admin/teams/1',
            '/admin/users/1',
        ]
        register_user(app)
        client = login_as_user(app)

        for route in routes:
            r = client.get(route)
            assert r.status_code == 302
            assert r.location.startswith('http://localhost/login')

    destroy_ctfd(app)


def test_get_admin_as_user():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/admin')
        assert r.status_code == 302
        assert r.location.startswith('http://localhost/login')
    destroy_ctfd(app)
