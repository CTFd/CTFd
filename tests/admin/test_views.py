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
            '/admin/import',
            '/admin/export',
            '/admin/config',
            '/admin/pages',
            '/admin/teams',
            '/admin/users',
            '/admin',
            # '/admin/submissions/<submission_type>',
            '/admin/submissions',
            # '/admin/challenges/<int:challenge_id>',
            # '/admin/plugins/<plugin>',
            # '/admin/pages/<int:page_id>',
            # '/admin/teams/<int:team_id>',
            # '/admin/users/<int:user_id>',
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


def test_get_admin_statistics():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/statistics')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_notifications():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/notifications')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_pages():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_pages_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages/new')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_users():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/users')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_users_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/users/new')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_teams():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/teams')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_teams_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/teams/new')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_scoreboard():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_challenges():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_challenges_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges/new')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions_correct():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions/correct')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions_incorrect():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/submissions/incorrect')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_submissions_incorrect():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/config')
        assert r.status_code == 200
    destroy_ctfd(app)
