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
