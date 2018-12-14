#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from jinja2.sandbox import SecurityError


def test_themes_run_in_sandbox():
    """Does get_config and set_config work properly"""
    app = create_ctfd()
    with app.app_context():
        try:
            app.jinja_env.from_string("{{ ().__class__.__bases__[0].__subclasses__()[40]('./test_utils.py').read() }}").render()
        except SecurityError:
            pass
        except Exception as e:
            raise e
    destroy_ctfd(app)


def test_themes_cant_access_configpy_attributes():
    """Themes should not be able to access config.py attributes"""
    app = create_ctfd()
    with app.app_context():
        assert app.config['SECRET_KEY'] == 'AAAAAAAAAAAAAAAAAAAA'
        assert app.jinja_env.from_string("{{ get_config('SECRET_KEY') }}").render() != app.config['SECRET_KEY']
    destroy_ctfd(app)


def test_themes_escape_html():
    """Themes should escape XSS properly"""
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db, name="<script>alert(1)</script>")
        user.affiliation = "<script>alert(1)</script>"
        user.website = "<script>alert(1)</script>"
        user.country = "<script>alert(1)</script>"

        with app.test_client() as client:
            r = client.get('/users')
            assert r.status_code == 200
            assert "<script>alert(1)</script>" not in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_custom_css():
    """Config should be able to properly set CSS"""
    app = create_ctfd()
    with app.app_context():

        with login_as_user(app, "admin") as admin:
            css_value = """.test{}"""
            css_value2 = """.test2{}"""
            r = admin.patch('/api/v1/configs', json={"css": css_value})
            assert r.status_code == 200
            assert get_config('css') == css_value

            r = admin.get('/static/user.css')
            assert r.get_data(as_text=True) == css_value

            r = admin.patch('/api/v1/configs', json={"css": css_value2})
            r = admin.get('/static/user.css')
            assert r.get_data(as_text=True) == css_value2
    destroy_ctfd(app)


def test_that_ctfd_can_be_deployed_in_subdir():
    """Test that CTFd can be deployed in a subdirectory"""
    # This test is quite complicated. I do not suggest modifying it haphazardly.
    app = create_ctfd(setup=False, application_root='/ctf')
    true_app = app.wsgi_app.mounts['/ctf']
    with app.app_context():
        with app.test_client() as client, true_app.test_client() as true_client:
            r = client.get('/setup')
            assert r.status_code == 302
            assert r.location == 'http://localhost/ctf/setup'

            r = true_client.get('/setup')
            with true_client.session_transaction() as sess:
                data = {
                    "ctf_name": 'name',
                    "name": 'admin',
                    "email": 'admin@ctfd.io',
                    "password": 'password',
                    "user_mode": 'users',
                    "nonce": sess.get('nonce')
                }
            r = true_client.post('/setup', data=data)
            assert r.status_code == 302
            assert r.location == 'http://localhost/ctf/'

            r = client.get('/challenges')
            assert r.status_code == 302
            assert r.location == 'http://localhost/ctf/challenges'

            r = client.get('/ctf/challenges')
            assert r.status_code == 302
            assert r.location == 'http://localhost/ctf/login?next=%2Fctf%2Fchallenges'
            r = client.get('/ctf/scoreboard')
            assert r.status_code == 200
    destroy_ctfd(true_app)
