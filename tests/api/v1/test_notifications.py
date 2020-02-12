#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Notifications
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_notification,
    login_as_user,
    register_user,
)


def test_api_notifications_get():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_notification(app.db)
        with login_as_user(app) as client:
            # test_api_notifications_get
            """Can the users get /api/v1/notifications"""
            r = client.get("/api/v1/notifications", json="")
            assert r.status_code == 200
            assert len(r.get_json()["data"]) == 1

            # test_api_get_notification_detail
            r = client.get("/api/v1/notifications/1", json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["title"] == "title"
            assert resp["data"]["content"] == "content"

            # test_api_notifications_post_non_admin
            """Can the users post /api/v1/notifications if not admin"""
            r = client.post("/api/v1/notifications", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_notifications_post_admin():
    """Can the users post /api/v1/notifications if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/notifications", json={"title": "title", "content": "content"}
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_delete_notifications_by_admin():
    """Test that an admin can delete notifications"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_notification(app.db)
        assert Notifications.query.count() == 1
        with login_as_user(app, name="admin") as client:
            r = client.delete("/api/v1/notifications/1", json="")
            assert r.status_code == 200
            assert r.get_json()["success"] is True
        assert Notifications.query.count() == 0
    destroy_ctfd(app)


def test_api_delete_notifications_by_user():
    """Test that a non-admin cannot delete notifications"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_challenge(app.db)
        gen_notification(app.db)
        assert Notifications.query.count() == 1
        with login_as_user(app) as client:
            r = client.delete("/api/v1/notifications/1", json="")
            assert r.status_code == 403
        assert Notifications.query.count() == 1
    destroy_ctfd(app)
