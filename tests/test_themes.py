#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

import pytest
from flask import render_template, render_template_string, request
from jinja2.exceptions import TemplateNotFound
from jinja2.sandbox import SecurityError
from werkzeug.test import Client

from CTFd.config import TestingConfig
from CTFd.utils import get_config, set_config
from tests.helpers import create_ctfd, destroy_ctfd, gen_user, login_as_user


def test_themes_run_in_sandbox():
    """Does get_config and set_config work properly"""
    app = create_ctfd()
    with app.app_context():
        try:
            app.jinja_env.from_string(
                "{{ ().__class__.__bases__[0].__subclasses__()[40]('./test_utils.py').read() }}"
            ).render()
        except SecurityError:
            pass
        except Exception as e:
            raise e
    destroy_ctfd(app)


def test_themes_cant_access_configpy_attributes():
    """Themes should not be able to access config.py attributes"""
    app = create_ctfd()
    with app.app_context():
        assert app.config["SECRET_KEY"] == "AAAAAAAAAAAAAAAAAAAA"
        assert (
            app.jinja_env.from_string("{{ get_config('SECRET_KEY') }}").render()
            != app.config["SECRET_KEY"]
        )
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
            r = client.get("/users")
            assert r.status_code == 200
            assert "<script>alert(1)</script>" not in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_theme_header():
    """Config should be able to properly set CSS in theme header"""
    app = create_ctfd()
    with app.app_context():

        with login_as_user(app, "admin") as admin:
            css_value = """.test{}"""
            css_value2 = """.test2{}"""
            r = admin.patch("/api/v1/configs", json={"theme_header": css_value})
            assert r.status_code == 200
            assert get_config("theme_header") == css_value

            r = admin.get("/")
            assert css_value in r.get_data(as_text=True)

            r = admin.patch("/api/v1/configs", json={"theme_header": css_value2})
            r = admin.get("/")
            assert css_value2 in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_that_ctfd_can_be_deployed_in_subdir():
    """Test that CTFd can be deployed in a subdirectory"""
    # This test is quite complicated. I do not suggest modifying it haphazardly.
    # Flask is automatically inserting the APPLICATION_ROOT into the
    # test urls which means when we hit /setup we hit /ctf/setup.
    # You can use the raw Werkzeug client to bypass this as we do below.
    app = create_ctfd(setup=False, application_root="/ctf")
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/")
            assert r.status_code == 302
            assert r.location == "http://localhost/ctf/setup"

            r = client.get("/setup")
            with client.session_transaction() as sess:
                data = {
                    "ctf_name": "CTFd",
                    "ctf_description": "CTF description",
                    "name": "admin",
                    "email": "admin@examplectf.com",
                    "password": "password",
                    "user_mode": "users",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/setup", data=data)
            assert r.status_code == 302
            assert r.location == "http://localhost/ctf/"

            c = Client(app)
            response = c.get("/")
            headers = dict(response.headers)
            assert response.status == "302 FOUND"
            assert headers["Location"] == "http://localhost/ctf/"

            r = client.get("/challenges")
            assert r.status_code == 200
            assert "Challenges" in r.get_data(as_text=True)

            r = client.get("/scoreboard")
            assert r.status_code == 200
            assert "Scoreboard" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_that_request_path_hijacking_works_properly():
    """Test that the CTFdRequest subclass correctly mimics the Flask Request when it should"""
    app = create_ctfd(setup=False, application_root="/ctf")
    assert app.request_class.__name__ == "CTFdRequest"
    with app.app_context():
        # Despite loading /challenges request.path should actually be /ctf/challenges because we are
        # preprending script_root and the test context already accounts for the application_root
        with app.test_request_context("/challenges"):
            assert request.path == "/ctf/challenges"
    destroy_ctfd(app)

    app = create_ctfd()
    assert app.request_class.__name__ == "CTFdRequest"
    with app.app_context():
        # Under normal circumstances we should be an exact clone of BaseRequest
        with app.test_request_context("/challenges"):
            assert request.path == "/challenges"

        from flask import Flask

        test_app = Flask("test")
        assert test_app.request_class.__name__ == "Request"
        with test_app.test_request_context("/challenges"):
            assert request.path == "/challenges"
    destroy_ctfd(app)


def test_theme_fallback_config():
    """Test that the `THEME_FALLBACK` config properly falls themes back to the core theme"""

    class ThemeFallbackConfig(TestingConfig):
        THEME_FALLBACK = False

    app = create_ctfd(config=ThemeFallbackConfig)
    # Make an empty theme
    try:
        os.mkdir(os.path.join(app.root_path, "themes", "foo_fallback"))
    except OSError:
        pass

    # Without theme fallback, missing themes should disappear
    with app.app_context():
        app.config["THEME_FALLBACK"] = False
        set_config("ctf_theme", "foo_fallback")
        assert app.config["THEME_FALLBACK"] == False
        with app.test_client() as client:
            try:
                r = client.get("/")
            except TemplateNotFound:
                pass
            try:
                r = client.get("/themes/foo_fallback/static/js/pages/main.dev.js")
            except TemplateNotFound:
                pass
    destroy_ctfd(app)

    app = create_ctfd()
    with app.app_context():
        set_config("ctf_theme", "foo_fallback")
        assert app.config["THEME_FALLBACK"] == True
        with app.test_client() as client:
            r = client.get("/")
            assert r.status_code == 200
            r = client.get("/themes/foo_fallback/static/js/pages/main.dev.js")
            assert r.status_code == 200
    destroy_ctfd(app)

    # Remove empty theme
    os.rmdir(os.path.join(app.root_path, "themes", "foo_fallback"))


def test_theme_template_loading_by_prefix():
    """Test that we can load theme files by their folder prefix"""
    app = create_ctfd()
    with app.test_request_context():
        tpl1 = render_template_string("{% extends 'core/page.html' %}", content="test")
        tpl2 = render_template("page.html", content="test")
        assert tpl1 == tpl2


def test_theme_template_disallow_loading_admin_templates():
    """Test that admin files in a theme will not be loaded"""
    app = create_ctfd()
    with app.app_context():
        try:
            # Make an empty malicious theme
            filename = os.path.join(
                app.root_path, "themes", "foo_disallow", "admin", "malicious.html"
            )
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            set_config("ctf_theme", "foo_disallow")
            with open(filename, "w") as f:
                f.write("malicious")

            with pytest.raises(TemplateNotFound):
                render_template_string("{% include 'admin/malicious.html' %}")
        finally:
            # Remove empty theme
            shutil.rmtree(
                os.path.join(app.root_path, "themes", "foo_disallow"),
                ignore_errors=True,
            )
