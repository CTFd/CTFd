#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_api_notifications_get():
    """Can the users get /api/v1/notifications"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app) as client:
            r = client.get('/api/v1/notifications', json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_notifications_post_non_admin():
    """Can the users post /api/v1/notifications if not admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app) as client:
            r = client.post('/api/v1/notifications', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_notifications_post_admin():
    """Can the users post /api/v1/notifications if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post('/api/v1/notifications', json={
                "title": "title",
                "content": "content"})
            assert r.status_code == 200
    destroy_ctfd(app)
