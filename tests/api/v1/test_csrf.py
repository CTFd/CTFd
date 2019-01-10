#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.testing import FlaskClient
from tests.helpers import *


def test_api_csrf_failure():
    """Can a user post /api/v1/awards if not admin"""
    app = create_ctfd()
    app.test_client_class = FlaskClient
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            r = client.post(
                '/api/v1/challenges',
                json={
                    "name": "chal",
                    "category": "cate",
                    "description": "desc",
                    "value": "100",
                    "state": "hidden",
                    "type": "standard"
                }
            )
            assert r.status_code == 403

            with client.session_transaction() as sess:
                nonce = sess.get('nonce')

            r = client.post(
                '/api/v1/challenges',
                headers={
                    'CSRF-Token': nonce
                },
                json={
                    "name": "chal",
                    "category": "cate",
                    "description": "desc",
                    "value": "100",
                    "state": "hidden",
                    "type": "standard"
                }
            )
            assert r.status_code == 200
    destroy_ctfd(app)
