#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_themes_handler():
    """Test that the themes handler is working properly"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/themes/core/static/css/style.css')
            assert r.status_code == 200
            r = client.get('/themes/core/static/css/404_NOT_FOUND')
            assert r.status_code == 404
            r = client.get('/themes/core/static/%2e%2e/%2e%2e/%2e%2e/utils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/%2e%2e%2f%2e%2e%2f%2e%2e%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/..%2f..%2f..%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/../../../utils.py')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_pages_routing_and_rendering():
    """Test that pages are routing and rendering"""
    app = create_ctfd()
    with app.app_context():
        html = '''##The quick brown fox jumped over the lazy dog'''
        route = 'test'
        title = 'Test'
        page = gen_page(app.db, title, route, html)

        with app.test_client() as client:
            r = client.get('/test')
            output = r.get_data(as_text=True)
            assert "<h2>The quick brown fox jumped over the lazy dog</h2>" in output
    destroy_ctfd(app)


def test_user_get_profile():
    """Can a registered user load their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_set_profile():
    """Can a registered user set their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        with client.session_transaction() as sess:
            data = {
                'name': 'user',
                'email': 'user@ctfd.io',
                # 'confirm': '',
                # 'password': '',
                'affiliation': 'affiliation_test',
                'website': 'https://ctfd.io',
                'country': 'US',
            }

        r = client.patch('/api/v1/users/me', json=data)
        assert r.status_code == 200

        user = Users.query.filter_by(id=2).first()
        assert user.affiliation == 'affiliation_test'
        assert user.website == 'https://ctfd.io'
        assert user.country == 'US'
    destroy_ctfd(app)
