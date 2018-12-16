#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import url_for
from tests.helpers import *
from freezegun import freeze_time
from CTFd.utils import set_config
import os


def test_index():
    """Does the index page return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_page():
    """Test that users can access pages that are created in the database"""
    app = create_ctfd()
    with app.app_context():
        gen_page(app.db, title="Title", route="this-is-a-route", content="This is some HTML")

        with app.test_client() as client:
            r = client.get('/this-is-a-route')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_draft_pages():
    """Test that draft pages can't be seen"""
    app = create_ctfd()
    with app.app_context():
        gen_page(app.db, title="Title", route="this-is-a-route", content="This is some HTML", draft=True)

        with app.test_client() as client:
            r = client.get('/this-is-a-route')
            assert r.status_code == 404

        register_user(app)
        client = login_as_user(app)
        r = client.get('/this-is-a-route')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_page_requiring_auth():
    """Test that pages properly require authentication"""
    app = create_ctfd()
    with app.app_context():
        gen_page(app.db, title="Title", route="this-is-a-route", content="This is some HTML", auth_required=True)

        with app.test_client() as client:
            r = client.get('/this-is-a-route')
            assert r.status_code == 302
            assert r.location == 'http://localhost/login?next=%2Fthis-is-a-route%3F'

        register_user(app)
        client = login_as_user(app)
        r = client.get('/this-is-a-route')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_not_found():
    """Should return a 404 for pages that are not found"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/this-should-404')
            assert r.status_code == 404
            r = client.post('/this-should-404')
            assert r.status_code == 404
    destroy_ctfd(app)


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


def test_user_can_access_files():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.uploads import rmdir
        chal = gen_challenge(app.db)
        chal_id = chal.id
        path = app.config.get('UPLOAD_FOLDER')

        location = os.path.join(path, 'test_file_path', 'test.txt')
        directory = os.path.dirname(location)
        model_path = os.path.join('test_file_path', 'test.txt')

        try:
            os.makedirs(directory)
            with open(location, 'wb') as obj:
                obj.write('testing file load'.encode())
            f = gen_file(app.db, location=model_path, challenge_id=chal_id)
            url = url_for('views.files', path=model_path)

            # Unauthed user should be able to see challenges if challenges are public
            set_config('challenge_visibility', 'public')
            with app.test_client() as client:
                r = client.get(url)

                assert r.status_code == 200
                assert r.get_data(as_text=True) == 'testing file load'

            # Unauthed user should be able to see challenges if challenges are private
            set_config('challenge_visibility', 'private')
            with app.test_client() as client:
                r = client.get(url)

                assert r.status_code == 403
                assert r.get_data(as_text=True) != 'testing file load'

            # Authed user should be able to see files if challenges are private
            register_user(app)
            client = login_as_user(app)
            r = client.get(url)
            assert r.status_code == 200
            assert r.get_data(as_text=True) == 'testing file load'

            with freeze_time("2017-10-7"):
                set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                for v in ('public', 'private'):
                    set_config('challenge_visibility', v)

                    # Unauthed users shouldn't be able to see files if the CTF hasn't started
                    client = app.test_client()
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != 'testing file load'

                    # Authed users shouldn't be able to see files if the CTF hasn't started
                    client = login_as_user(app)
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != 'testing file load'

                    # Admins should be able to see files if the CTF hasn't started
                    admin = login_as_user(app, "admin")
                    r = admin.get(url)
                    assert r.status_code == 200
                    assert r.get_data(as_text=True) == 'testing file load'
        finally:
            rmdir(directory)
    destroy_ctfd(app)
