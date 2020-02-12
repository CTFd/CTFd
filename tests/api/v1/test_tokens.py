#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from CTFd.models import Tokens, Users
from CTFd.schemas.tokens import TokenSchema
from CTFd.utils.security.auth import generate_user_token
from tests.helpers import create_ctfd, destroy_ctfd, gen_user, login_as_user


def test_api_tag_list_post():
    """Can a user create a token"""
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db, name="user")
        user_id = user.id
        with login_as_user(app) as client:
            r = client.post("/api/v1/tokens", json={})
            assert r.status_code == 200
            resp = r.get_json()
            value = resp["data"]["value"]
            token = Tokens.query.filter_by(value=value).first()
            assert token.user_id == user_id
            assert token.expiration > datetime.datetime.utcnow()

            data = {"expiration": "9999-12-30"}
            r = client.post("/api/v1/tokens", json=data)
            assert r.status_code == 200
            resp = r.get_json()
            value = resp["data"]["value"]
            token = Tokens.query.filter_by(value=value).first()
            assert token.user_id == user_id
            assert token.expiration.year == 9999
    destroy_ctfd(app)


def test_api_tag_list_get():
    """Can a user get /api/v1/tokens"""
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db, name="user")
        generate_user_token(user)

        user2 = gen_user(app.db, name="user2", email="user2@ctfd.io")
        generate_user_token(user2)
        generate_user_token(user2)
        with login_as_user(app) as client:
            r = client.get("/api/v1/tokens", json="")
            assert r.status_code == 200
            resp = r.get_json()
            len(resp["data"]) == 1

        with login_as_user(app, name="user2") as client:
            r = client.get("/api/v1/tokens", json="")
            assert r.status_code == 200
            resp = r.get_json()
            len(resp["data"]) == 2
    destroy_ctfd(app)


def test_api_tag_detail_get():
    """Can a user get /api/v1/tokens/<token_id>"""
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db, name="user")
        generate_user_token(user)

        with login_as_user(app) as client:
            r = client.get("/api/v1/tokens/1", json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert sorted(resp["data"].keys()) == sorted(TokenSchema().views["user"])

        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/tokens/1", json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert sorted(resp["data"].keys()) == sorted(TokenSchema().views["admin"])

        gen_user(app.db, name="user2", email="user2@ctfd.io")
        with login_as_user(app, "user2") as client:
            r = client.get("/api/v1/tokens/1", json="")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_token_delete():
    """Can tokens be deleted by owners, and admins"""
    app = create_ctfd()
    with app.app_context():
        # Can be deleted by the user
        user = gen_user(app.db)
        user_id = user.id
        username = user.name
        token = generate_user_token(user)
        token_id = token.id
        with login_as_user(app, username) as client:
            r = client.delete("/api/v1/tokens/" + str(token_id), json="")
            assert r.status_code == 200
            assert Tokens.query.count() == 0

        # Can be deleted by admins
        user = Users.query.filter_by(id=user_id).first()
        token = generate_user_token(user)
        token_id = token.id
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/tokens/" + str(token_id), json="")
            assert r.status_code == 200
            assert Tokens.query.count() == 0

        # First user
        first_user = Users.query.filter_by(id=user_id).first()
        token = generate_user_token(first_user)
        token_id = token.id
        # Second user
        second_user = gen_user(app.db, name="user2", email="user2@ctfd.io")
        username2 = second_user.name
        with login_as_user(app, username2) as client:
            r = client.delete("/api/v1/tokens/" + str(token_id), json="")
            assert r.status_code == 404
            assert Tokens.query.count() == 1
    destroy_ctfd(app)
