#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time

from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_user,
    login_as_user,
    register_user,
)


def test_api_challenge_list_visibility():
    """Can the api load /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_list_ctftime():
    """Can the api load /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_list_user_visibility():
    """Can the user load /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_list_user_ctftime():
    """Can the user load /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_list_verified_emails():
    """Can a verified email load /api/v1/challenges"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("verify_emails", True)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 302
        gen_user(
            app.db,
            name="user_name",
            email="verified_user@ctfd.io",
            password="password",
            verified=True,
        )
        registered_client = login_as_user(app, "user_name", "password")
        r = registered_client.get("/api/v1/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_visibility():
    """Can the api load /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            gen_challenge(app.db)
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_ctftime():
    """Can the api load /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_user_visibility():
    """Can the user load /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_user_ctftime():
    """Can the user load /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_verified_emails():
    """Can a verified email load /api/v1/challenges/<challenge_id>"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("verify_emails", True)
        gen_challenge(app.db)
        gen_user(
            app.db,
            name="user_name",
            email="verified_user@ctfd.io",
            password="password",
            verified=True,
        )
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, "user_name", "password")
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 302
        r = registered_client.get("/api/v1/challenges/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id> 404"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_solves_visibility():
    """Can the api load /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_solves_ctftime():
    """Can the api load /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_solves_user_visibility():
    """Can the user load /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_solves_user_ctftime():
    """Can the user load /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_solves_verified_emails():
    """Can a verified email load /api/v1/challenges/<challenge_id>/solves"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("verify_emails", True)
        gen_challenge(app.db)
        gen_user(
            app.db,
            name="user_name",
            email="verified_user@ctfd.io",
            password="password",
            verified=True,
        )
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, "user_name", "password")
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 302
        r = registered_client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_solves_score_visibility():
    """Can a user load /api/v1/challenges/<challenge_id>/solves if score_visibility is public/private/admin"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("challenge_visibility", "public")
        set_config("score_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 200
        set_config("challenge_visibility", "private")
        set_config("score_visibility", "private")
        register_user(app)
        private_client = login_as_user(app)
        r = private_client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
        set_config("score_visibility", "admins")
        admin = login_as_user(app, "admin", "password")
        r = admin.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_solves_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id>/solves 404"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 404
    destroy_ctfd(app)
