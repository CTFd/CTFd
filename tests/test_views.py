#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask import url_for
from freezegun import freeze_time

from CTFd.cache import clear_pages
from CTFd.utils import set_config
from CTFd.utils.config.pages import get_pages
from CTFd.utils.encoding import hexencode
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_file,
    gen_page,
    login_as_user,
    register_user,
)


def test_index():
    """Does the index page return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_page():
    """Test that users can access pages that are created in the database"""
    app = create_ctfd()
    with app.app_context():
        gen_page(
            app.db, title="Title", route="this-is-a-route", content="This is some HTML"
        )

        with app.test_client() as client:
            r = client.get("/this-is-a-route")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_draft_pages():
    """Test that draft pages can't be seen"""
    app = create_ctfd()
    with app.app_context():
        gen_page(
            app.db,
            title="Title",
            route="this-is-a-route",
            content="This is some HTML",
            draft=True,
        )

        with app.test_client() as client:
            r = client.get("/this-is-a-route")
            assert r.status_code == 404

        register_user(app)
        client = login_as_user(app)
        r = client.get("/this-is-a-route")
        assert r.status_code == 404
    destroy_ctfd(app)


def test_page_requiring_auth():
    """Test that pages properly require authentication"""
    app = create_ctfd()
    with app.app_context():
        gen_page(
            app.db,
            title="Title",
            route="this-is-a-route",
            content="This is some HTML",
            auth_required=True,
        )

        with app.test_client() as client:
            r = client.get("/this-is-a-route")
            assert r.status_code == 302
            assert r.location == "http://localhost/login?next=%2Fthis-is-a-route%3F"

        register_user(app)
        client = login_as_user(app)
        r = client.get("/this-is-a-route")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_hidden_pages():
    """Test that hidden pages aren't on the navbar but can be loaded"""
    app = create_ctfd()
    with app.app_context():
        page = gen_page(
            app.db,
            title="HiddenPageTitle",
            route="this-is-a-hidden-route",
            content="This is some HTML",
            hidden=True,
        )
        clear_pages()
        assert page not in get_pages()

        with app.test_client() as client:
            r = client.get("/")
            assert r.status_code == 200
            assert "HiddenPageTitle" not in r.get_data(as_text=True)

        with app.test_client() as client:
            r = client.get("/this-is-a-hidden-route")
            assert r.status_code == 200
            assert "This is some HTML" in r.get_data(as_text=True)
    destroy_ctfd(app)


def test_not_found():
    """Should return a 404 for pages that are not found"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/this-should-404")
            assert r.status_code == 404
            r = client.post("/this-should-404")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_themes_handler():
    """Test that the themes handler is working properly"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/themes/core/static/css/main.min.css")
            assert r.status_code == 200
            r = client.get("/themes/core/static/css/404_NOT_FOUND")
            assert r.status_code == 404
            r = client.get("/themes/core/static/%2e%2e/%2e%2e/%2e%2e/utils.py")
            assert r.status_code == 404
            r = client.get("/themes/core/static/%2e%2e%2f%2e%2e%2f%2e%2e%2futils.py")
            assert r.status_code == 404
            r = client.get("/themes/core/static/..%2f..%2f..%2futils.py")
            assert r.status_code == 404
            r = client.get("/themes/core/static/../../../utils.py")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_pages_routing_and_rendering():
    """Test that pages are routing and rendering"""
    app = create_ctfd()
    with app.app_context():
        html = """## The quick brown fox jumped over the lazy dog"""
        route = "test"
        title = "Test"
        gen_page(app.db, title, route, html)

        with app.test_client() as client:
            r = client.get("/test")
            output = r.get_data(as_text=True)
            print(output)
            assert "<h2>The quick brown fox jumped over the lazy dog</h2>" in output
    destroy_ctfd(app)


def test_user_get_profile():
    """Can a registered user load their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/profile")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_can_access_files():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.uploads import rmdir

        chal = gen_challenge(app.db)
        chal_id = chal.id
        path = app.config.get("UPLOAD_FOLDER")

        location = os.path.join(path, "test_file_path", "test.txt")
        directory = os.path.dirname(location)
        model_path = os.path.join("test_file_path", "test.txt")

        try:
            os.makedirs(directory)
            with open(location, "wb") as obj:
                obj.write("testing file load".encode())
            gen_file(app.db, location=model_path, challenge_id=chal_id)
            url = url_for("views.files", path=model_path)

            # Unauthed user should be able to see challenges if challenges are public
            set_config("challenge_visibility", "public")
            with app.test_client() as client:
                r = client.get(url)

                assert r.status_code == 200
                assert r.get_data(as_text=True) == "testing file load"

            # Unauthed user should not be able to see challenges if challenges are private
            set_config("challenge_visibility", "private")
            with app.test_client() as client:
                r = client.get(url)

                assert r.status_code == 403
                assert r.get_data(as_text=True) != "testing file load"

            # Authed user should be able to see files if challenges are private
            register_user(app)
            client = login_as_user(app)
            r = client.get(url)
            assert r.status_code == 200
            assert r.get_data(as_text=True) == "testing file load"

            with freeze_time("2017-10-5"):
                # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                set_config("start", "1507262400")
                for v in ("public", "private"):
                    set_config("challenge_visibility", v)

                    # Unauthed users shouldn't be able to see files if the CTF hasn't started
                    client = app.test_client()
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                    # Authed users shouldn't be able to see files if the CTF hasn't started
                    client = login_as_user(app)
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                    # Admins should be able to see files if the CTF hasn't started
                    admin = login_as_user(app, "admin")
                    r = admin.get(url)
                    assert r.status_code == 200
                    assert r.get_data(as_text=True) == "testing file load"

            with freeze_time("2017-10-7"):
                # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                set_config("end", "1507262400")
                for v in ("public", "private"):
                    set_config("challenge_visibility", v)

                    # Unauthed users shouldn't be able to see files if the CTF has ended
                    client = app.test_client()
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                    # Authed users shouldn't be able to see files if the CTF has ended
                    client = login_as_user(app)
                    r = client.get(url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                    # Admins should be able to see files if the CTF has ended
                    admin = login_as_user(app, "admin")
                    r = admin.get(url)
                    assert r.status_code == 200
                    assert r.get_data(as_text=True) == "testing file load"
        finally:
            rmdir(directory)
    destroy_ctfd(app)


def test_user_can_access_files_with_auth_token():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.uploads import rmdir

        chal = gen_challenge(app.db)
        chal_id = chal.id
        path = app.config.get("UPLOAD_FOLDER")

        md5hash = hexencode(os.urandom(16))

        location = os.path.join(path, md5hash, "test.txt")
        directory = os.path.dirname(location)
        model_path = os.path.join(md5hash, "test.txt")

        try:
            os.makedirs(directory)
            with open(location, "wb") as obj:
                obj.write("testing file load".encode())
            gen_file(app.db, location=model_path, challenge_id=chal_id)
            url = url_for("views.files", path=model_path)

            register_user(app)
            with login_as_user(app) as client:
                req = client.get("/api/v1/challenges/1")
                data = req.get_json()
                file_url = data["data"]["files"][0]

            with app.test_client() as client:
                r = client.get(url)
                assert r.status_code == 403
                assert r.get_data(as_text=True) != "testing file load"

                r = client.get(
                    url_for(
                        "views.files",
                        path=model_path,
                        token="random_token_that_shouldnt_work",
                    )
                )
                assert r.status_code == 403
                assert r.get_data(as_text=True) != "testing file load"

                r = client.get(file_url)
                assert r.status_code == 200
                assert r.get_data(as_text=True) == "testing file load"

                # Unauthed users shouldn't be able to see files if the CTF is admins only
                set_config("challenge_visibility", "admins")
                r = client.get(file_url)
                assert r.status_code == 403
                assert r.get_data(as_text=True) != "testing file load"
                set_config("challenge_visibility", "private")

                with freeze_time("2017-10-5"):
                    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                    set_config("start", "1507262400")

                    # Unauthed users shouldn't be able to see files if the CTF hasn't started
                    r = client.get(file_url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                with freeze_time("2017-10-5"):
                    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                    set_config("start", "1507262400")
                    for v in ("public", "private"):
                        set_config("challenge_visibility", v)

                        # Unauthed users shouldn't be able to see files if the CTF hasn't started
                        client = app.test_client()
                        r = client.get(file_url)
                        assert r.status_code == 403
                        assert r.get_data(as_text=True) != "testing file load"

                        # Authed users shouldn't be able to see files if the CTF hasn't started
                        client = login_as_user(app)
                        r = client.get(file_url)
                        assert r.status_code == 403
                        assert r.get_data(as_text=True) != "testing file load"

                        # Admins should be able to see files if the CTF hasn't started
                        admin = login_as_user(app, "admin")
                        r = admin.get(file_url)
                        assert r.status_code == 200
                        assert r.get_data(as_text=True) == "testing file load"

                with freeze_time("2017-10-7"):
                    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                    set_config("end", "1507262400")
                    for v in ("public", "private"):
                        set_config("challenge_visibility", v)

                        # Unauthed users shouldn't be able to see files if the CTF has ended
                        client = app.test_client()
                        r = client.get(file_url)
                        assert r.status_code == 403
                        assert r.get_data(as_text=True) != "testing file load"

                        # Authed users shouldn't be able to see files if the CTF has ended
                        client = login_as_user(app)
                        r = client.get(file_url)
                        assert r.status_code == 403
                        assert r.get_data(as_text=True) != "testing file load"

                        # Admins should be able to see files if the CTF has ended
                        admin = login_as_user(app, "admin")
                        r = admin.get(file_url)
                        assert r.status_code == 200
                        assert r.get_data(as_text=True) == "testing file load"

                with freeze_time("2017-10-7"):
                    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                    set_config("end", "1507262400")
                    set_config("view_after_ctf", True)
                    for v in ("public", "private"):
                        set_config("challenge_visibility", v)

                        # Unauthed users should be able to download if view_after_ctf
                        client = app.test_client()
                        r = client.get(file_url)
                        assert r.status_code == 200
                        assert r.get_data(as_text=True) == "testing file load"
        finally:
            rmdir(directory)
    destroy_ctfd(app)


def test_user_can_access_files_if_view_after_ctf():
    app = create_ctfd()
    with app.app_context():
        from CTFd.utils.uploads import rmdir

        chal = gen_challenge(app.db)
        chal_id = chal.id
        path = app.config.get("UPLOAD_FOLDER")

        md5hash = hexencode(os.urandom(16))

        location = os.path.join(path, md5hash, "test.txt")
        directory = os.path.dirname(location)
        model_path = os.path.join(md5hash, "test.txt")

        try:
            os.makedirs(directory)
            with open(location, "wb") as obj:
                obj.write("testing file load".encode())
            gen_file(app.db, location=model_path, challenge_id=chal_id)

            register_user(app)
            with login_as_user(app) as client:
                req = client.get("/api/v1/challenges/1")
                data = req.get_json()
                file_url = data["data"]["files"][0]

                # After ctf end
                with freeze_time("2017-10-7"):
                    # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
                    set_config("end", "1507262400")

                    r = client.get(file_url)
                    assert r.status_code == 403
                    assert r.get_data(as_text=True) != "testing file load"

                    set_config("view_after_ctf", True)
                    r = client.get(file_url)
                    assert r.status_code == 200
                    assert r.get_data(as_text=True) == "testing file load"

                    # Unauthed users should be able to download if view_after_ctf
                    client = app.test_client()
                    r = client.get(file_url)
                    assert r.status_code == 200
                    assert r.get_data(as_text=True) == "testing file load"
        finally:
            rmdir(directory)

    destroy_ctfd(app)


def test_robots_txt():
    """Does the robots.txt page work"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/robots.txt")
            assert r.status_code == 200
            assert r.get_data(as_text=True) == "User-agent: *\nDisallow: /admin\n"
        set_config("robots_txt", "testing")
        with app.test_client() as client:
            r = client.get("/robots.txt")
            assert r.status_code == 200
            assert r.get_data(as_text=True) == "testing"
    destroy_ctfd(app)
