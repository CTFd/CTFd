#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_topic,
    login_as_user,
    register_user,
)


def test_api_topics_non_admin():
    """Can a user interact with /api/v1/topics if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        with app.test_client() as client:
            r = client.get("/api/v1/topics", json="")
            assert r.status_code == 403

            """Can a user post /api/v1/topics if not admin"""
            r = client.post("/api/v1/topics")
            assert r.status_code == 403

            """Can a user delete /api/v1/topics if not admin"""
            r = client.delete("/api/v1/topics")
            assert r.status_code == 403

            """Can a user get /api/v1/topics/<topic_id> if not admin"""
            r = client.get("/api/v1/topics/1", json="")
            assert r.status_code == 403

            """Can a user delete /api/v1/topics/<topic_id> if not admin"""
            r = client.delete("/api/v1/topics/1", json="")
            assert r.status_code == 403

        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/topics", json="")
            assert r.status_code == 403

            """Can a user post /api/v1/topics if not admin"""
            r = client.post("/api/v1/topics")
            assert r.status_code == 403

            """Can a user delete /api/v1/topics if not admin"""
            r = client.delete("/api/v1/topics")
            assert r.status_code == 403

            """Can a user get /api/v1/topics/<topic_id> if not admin"""
            r = client.get("/api/v1/topics/1", json="")
            assert r.status_code == 403

            """Can a user delete /api/v1/topics/<topic_id> if not admin"""
            r = client.delete("/api/v1/topics/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_topics_get_admin():
    """Can a user get /api/v1/topics if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        gen_topic(app.db, challenge_id=1, value="topic2")
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/topics")
            assert r.status_code == 200
            assert r.get_json() == {
                "success": True,
                "data": [{"id": 1, "value": "topic"}, {"id": 2, "value": "topic2"}],
            }
    destroy_ctfd(app)


def test_api_topics_post_admin():
    """Can a user post /api/v1/topics if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/topics",
                json={"value": "topic", "type": "challenge", "challenge_id": 1},
            )
            assert r.status_code == 200
            print(r.get_json())
            assert r.get_json() == {
                "success": True,
                "data": {
                    "challenge_id": 1,
                    "challenge": 1,
                    "topic": 1,
                    "id": 1,
                    "topic_id": 1,
                },
            }
    destroy_ctfd(app)


def test_api_topics_delete_admin():
    """Can a user delete /api/v1/topics/<topic_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/topics/1", json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp.get("data") is None
            assert resp.get("success") is True
    destroy_ctfd(app)


def test_api_topics_delete_target_admin():
    """Can a user delete /api/v1/topics if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/topics?type=challenge&target_id=1", json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp.get("data") is None
            assert resp.get("success") is True
    destroy_ctfd(app)
