#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.plugins import (
    bypass_csrf_protection,
    get_admin_plugin_menu_bar,
    get_user_page_menu_bar,
    override_template,
    register_admin_plugin_menu_bar,
    register_admin_plugin_script,
    register_admin_plugin_stylesheet,
    register_plugin_asset,
    register_plugin_assets_directory,
    register_plugin_script,
    register_user_page_menu_bar,
)
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    login_as_user,
    setup_ctfd,
)


def test_register_plugin_asset():
    """Test that plugin asset registration works"""
    app = create_ctfd(setup=False)
    register_plugin_asset(app, asset_path="/plugins/__init__.py")
    app = setup_ctfd(app)
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/plugins/__init__.py")
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
    destroy_ctfd(app)


def test_register_plugin_assets_directory():
    """Test that plugin asset directory registration works"""
    app = create_ctfd(setup=False)
    register_plugin_assets_directory(app, base_path="/plugins/")
    app = setup_ctfd(app)
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/plugins/__init__.py")
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
            r = client.get("/plugins/challenges/__init__.py")
            assert len(r.get_data(as_text=True)) > 0
            assert r.status_code == 200
    destroy_ctfd(app)


def test_override_template():
    """Does override_template work properly for regular themes when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        override_template("login.html", "LOGIN OVERRIDE")
        with app.test_client() as client:
            r = client.get("/login")
            assert r.status_code == 200
            output = r.get_data(as_text=True)
            assert "LOGIN OVERRIDE" in output
    destroy_ctfd(app)


def test_admin_override_template():
    """Does override_template work properly for the admin panel when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        override_template("admin/users/user.html", "ADMIN USER OVERRIDE")

        client = login_as_user(app, name="admin", password="password")
        r = client.get("/admin/users/1")
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert "ADMIN USER OVERRIDE" in output
    destroy_ctfd(app)


def test_register_plugin_script():
    """Test that register_plugin_script adds script paths to the core theme when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        register_plugin_script("/fake/script/path.js")
        register_plugin_script("http://examplectf.com/fake/script/path.js")
        with app.test_client() as client:
            r = client.get("/")
            output = r.get_data(as_text=True)
            assert "/fake/script/path.js" in output
            assert "http://examplectf.com/fake/script/path.js" in output
    destroy_ctfd(app)


def test_register_plugin_stylesheet():
    """Test that register_plugin_stylesheet adds stylesheet paths to the core theme when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        register_plugin_script("/fake/stylesheet/path.css")
        register_plugin_script("http://examplectf.com/fake/stylesheet/path.css")
        with app.test_client() as client:
            r = client.get("/")
            output = r.get_data(as_text=True)
            assert "/fake/stylesheet/path.css" in output
            assert "http://examplectf.com/fake/stylesheet/path.css" in output
    destroy_ctfd(app)


def test_register_admin_plugin_script():
    """Test that register_admin_plugin_script adds script paths to the admin theme when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        register_admin_plugin_script("/fake/script/path.js")
        register_admin_plugin_script("http://examplectf.com/fake/script/path.js")
        with login_as_user(app, name="admin") as client:
            r = client.get("/admin/statistics")
            output = r.get_data(as_text=True)
            assert "/fake/script/path.js" in output
            assert "http://examplectf.com/fake/script/path.js" in output
    destroy_ctfd(app)


def test_register_admin_plugin_stylesheet():
    """Test that register_admin_plugin_stylesheet adds stylesheet paths to the admin theme when used from a plugin"""
    app = create_ctfd()
    with app.app_context():
        register_admin_plugin_stylesheet("/fake/stylesheet/path.css")
        register_admin_plugin_stylesheet(
            "http://examplectf.com/fake/stylesheet/path.css"
        )
        with login_as_user(app, name="admin") as client:
            r = client.get("/admin/statistics")
            output = r.get_data(as_text=True)
            assert "/fake/stylesheet/path.css" in output
            assert "http://examplectf.com/fake/stylesheet/path.css" in output
    destroy_ctfd(app)


def test_register_admin_plugin_menu_bar():
    """
    Test that register_admin_plugin_menu_bar() properly inserts into HTML and get_admin_plugin_menu_bar()
    returns the proper list.
    """
    app = create_ctfd()
    with app.app_context():
        register_admin_plugin_menu_bar(
            title="test_admin_plugin_name", route="/test_plugin"
        )

        client = login_as_user(app, name="admin", password="password")
        r = client.get("/admin/statistics")
        output = r.get_data(as_text=True)
        assert "/test_plugin" in output
        assert "test_admin_plugin_name" in output

        menu_item = get_admin_plugin_menu_bar()[0]
        assert menu_item.title == "test_admin_plugin_name"
        assert menu_item.route == "/test_plugin"
    destroy_ctfd(app)


def test_register_user_page_menu_bar():
    """
    Test that the register_user_page_menu_bar() properly inserts into HTML and get_user_page_menu_bar() returns the
    proper list.
    """
    app = create_ctfd()
    with app.app_context():
        register_user_page_menu_bar(
            title="test_user_menu_link", route="/test_user_href"
        )

        with app.test_client() as client:
            r = client.get("/")
            output = r.get_data(as_text=True)
            assert "/test_user_href" in output
            assert "test_user_menu_link" in output

        with app.test_request_context():
            menu_item = get_user_page_menu_bar()[0]
            assert menu_item.title == "test_user_menu_link"
            assert menu_item.route == "/test_user_href"
    destroy_ctfd(app)


def test_bypass_csrf_protection():
    """
    Test that the bypass_csrf_protection decorator functions properly
    """
    app = create_ctfd()

    with app.app_context():
        with app.test_client() as client:
            r = client.post("/login")
            output = r.get_data(as_text=True)
            assert r.status_code == 403

        def bypass_csrf_protection_test_route():
            return "Success", 200

        # Hijack an existing route to avoid any kind of hacks to create a test route
        app.view_functions["auth.login"] = bypass_csrf_protection(
            bypass_csrf_protection_test_route
        )

        with app.test_client() as client:
            r = client.post("/login")
            output = r.get_data(as_text=True)
            assert r.status_code == 200
            assert output == "Success"
    destroy_ctfd(app)


def test_challenges_model_access_plugin_class():
    """
    Test that the Challenges model can access its plugin class
    """
    app = create_ctfd()

    with app.app_context():
        from CTFd.plugins.challenges import get_chal_class

        chal = gen_challenge(app.db)
        assert chal.plugin_class == get_chal_class("standard")
    destroy_ctfd(app)
