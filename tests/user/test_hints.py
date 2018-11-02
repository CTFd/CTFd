#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_user_cannot_unlock_hint():
    """Test that a user can't unlock a hint if they don't have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            flag = gen_flag(app.db, challenge_id=chal.id, content='flag')

            hint = gen_hint(db, chal_id, cost=10)
            hint_id = hint.id

            client = login_as_user(app, name="user1", password="password")

            with client.session_transaction() as sess:
                r = client.get('/api/v1/hints/{}'.format(hint_id))
                resp = r.get_json()
                assert resp['data'].get('content') is None
                assert resp['data'].get('cost') == 10
    destroy_ctfd(app)


def test_user_can_unlock_hint():
    """Test that a user can unlock a hint if they have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            flag = gen_flag(app.db, challenge_id=chal.id, content='flag')

            hint = gen_hint(app.db, chal_id, cost=10)
            hint_id = hint.id

            award = gen_award(app.db, user_id=2, value=15)

            client = login_as_user(app, name="user1", password="password")

            user = Users.query.filter_by(name="user1").first()
            assert user.score == 15

            with client.session_transaction() as sess:
                r = client.get('/api/v1/hints/{}'.format(hint_id))
                resp = r.get_json()
                assert resp['data'].get('content') is None

                params = {
                    "target": hint_id,
                    "type": "hints"
                }

                r = client.post('/api/v1/unlocks', json=params)
                resp = r.get_json()
                assert resp['success'] is True

                r = client.get('/api/v1/hints/{}'.format(hint_id))
                resp = r.get_json()
                assert resp['data'].get('content')

                user = Users.query.filter_by(name="user1").first()
                assert user.score == 5
    destroy_ctfd(app)
