#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_api_awards_post_non_admin():
    """Can a user post /api/v1/awards if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.post('/api/v1/awards', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_awards_post_admin():
    """Can a user post /api/v1/awards if admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, 'admin') as client:
            r = client.post('/api/v1/awards', json={"name": "Name",
                                                    "value": "100",
                                                    "category": "Cate",
                                                    "description": "Desc",
                                                    "user_id": 2})
            assert r.status_code == 200
            assert r.get_json()['success'] is True
            r = client.post('/api/v1/awards', json="")
            assert r.status_code == 400
    destroy_ctfd(app)


def test_api_award_get_non_admin():
    """Can a user get /api/v1/awards/<award_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/awards/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_award_get_admin():
    """Can a user get /api/v1/awards/<award_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_award(app.db, 1)
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/awards/1', json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_award_delete_non_admin():
    """Can a user delete /api/v1/awards/<award_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.delete('/api/v1/awards/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_award_delete_admin():
    """Can a user delete /api/v1/awards/<award_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_award(app.db, 1)
        with login_as_user(app, 'admin') as client:
            r = client.delete('/api/v1/awards/1', json="")
            assert r.status_code == 200
    destroy_ctfd(app)
