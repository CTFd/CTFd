#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_user_get_scoreboard():
    """Can a registered user load /scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scores():
    """Can a registered user load /api/v1/scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_topteams():
    """Can a registered user load /api/v1/scoreboard/top/10"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/scoreboard/top/10')
        assert r.status_code == 200
    destroy_ctfd(app)
