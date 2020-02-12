#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_solve,
    login_as_user,
)


def test_api_submissions_get_non_admin():
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_solve(app.db, user_id=1)
        with app.test_client() as client:
            # test_api_submissions_get_non_admin
            """Can a user get /api/v1/submissions if not admin"""
            r = client.get("/api/v1/submissions", json="")
            assert r.status_code == 403

            # test_api_submissions_post_non_admin
            """Can a user post /api/v1/submissions if not admin"""
            r = client.post("/api/v1/submissions")
            assert r.status_code == 403

            # test_api_submission_get_non_admin
            """Can a user get /api/v1/submissions/<submission_id> if not admin"""
            r = client.get("/api/v1/submissions/1", json="")
            assert r.status_code == 403

            # test_api_submission_delete_non_admin
            """Can a user delete /api/v1/submissions/<submission_id> if not admin"""
            r = client.delete("/api/v1/submissions/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_submissions_get_admin():
    """Can a user get /api/v1/submissions if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/submissions", json="")
            assert r.status_code == 200
            r = client.get("/api/v1/submissions?user_id=1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submissions_post_admin():
    """Can a user post /api/v1/submissions if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/submissions",
                json={
                    "provided": "MARKED AS SOLVED BY ADMIN",
                    "user_id": 1,
                    "team_id": None,
                    "challenge_id": "1",
                    "type": "correct",
                },
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submission_get_admin():
    """Can a user get /api/v1/submissions/<submission_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_solve(app.db, user_id=1)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/submissions/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_submission_delete_admin():
    """Can a user patch /api/v1/submissions/<submission_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_solve(app.db, user_id=1)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/submissions/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
    destroy_ctfd(app)
