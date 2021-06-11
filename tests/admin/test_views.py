#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_page,
    gen_team,
    login_as_user,
    register_user,
)


def get_bp_urls(blueprint):
    temp_app = Flask(__name__)
    temp_app.register_blueprint(blueprint)
    return [str(p) for p in temp_app.url_map.iter_rules()]


def test_admin_access():
    """Can a user access admin pages?"""
    app = create_ctfd()
    with app.app_context():
        gen_page(app.db, title="title", route="/route", content="content")
        gen_challenge(app.db)
        gen_team(app.db)
        routes = [
            "/admin/challenges/new",
            "/admin/export/csv",
            # '/admin/pages/preview',
            "/admin/pages/new",
            "/admin/teams/new",
            "/admin/users/new",
            "/admin/notifications",
            "/admin/challenges",
            "/admin/scoreboard",
            "/admin/statistics",
            "/admin/export",
            "/admin/config",
            "/admin/pages",
            "/admin/teams",
            "/admin/users",
            "/admin",
            "/admin/submissions/correct",
            "/admin/submissions/incorrect",
            "/admin/submissions",
            "/admin/challenges/1",
            # '/admin/plugins/<plugin>',
            "/admin/pages/1",
            "/admin/teams/1",
            "/admin/users/1",
        ]
        register_user(app)
        client = login_as_user(app)

        for route in routes:
            r = client.get(route)
            assert r.status_code == 302
            assert r.location.startswith("http://localhost/login")

        admin = login_as_user(app, name="admin")
        routes.remove("/admin")
        routes.remove("/admin/export/csv")
        routes.remove("/admin/export")
        for route in routes:
            r = admin.get(route)
            assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_as_user():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/admin")
        assert r.status_code == 302
        assert r.location.startswith("http://localhost/login")
    destroy_ctfd(app)
