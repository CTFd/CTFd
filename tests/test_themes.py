#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from jinja2.sandbox import SecurityError
from werkzeug.test import Client

from CTFd.utils import get_config
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
                    "email": "admin@ctfd.io",
                    "password": "password",
                    "user_mode": "users",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/setup", data=data)
            assert r.status_code == 302
            assert r.location == "http://localhost/ctf/"

            c = Client(app)
            app_iter, status, headers = c.get("/")
            headers = dict(headers)
            assert status == "302 FOUND"
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
