#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge
from tests.helpers import *


def test_can_create_dynamic_challenge():
    """Test that dynamic challenges can be made from the API/admin panel"""
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "dynamic"
        }

        r = client.post('/api/v1/challenges', json=challenge_data)
        assert r.get_json().get('data')['id'] == 1

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        assert challenge.value == 100
        assert challenge.initial == 100
        assert challenge.decay == 20
        assert challenge.minimum == 1
    destroy_ctfd(app)


def test_can_update_dynamic_challenge():
    """Test that dynamic challenges can be deleted"""
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "dynamic"
        }
        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.create(req)

        assert challenge.value == 100
        assert challenge.initial == 100
        assert challenge.decay == 20
        assert challenge.minimum == 1

        challenge_data = {
            "name": "new_name",
            "category": "category",
            "description": "new_description",
            "value": "200",
            "initial": "200",
            "decay": "40",
            "minimum": "5",
            "max_attempts": "0",
            "state": "visible"
        }

        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.update(challenge, req)

        assert challenge.name == 'new_name'
        assert challenge.description == "new_description"
        assert challenge.value == 200
        assert challenge.initial == 200
        assert challenge.decay == 40
        assert challenge.minimum == 5
        assert challenge.state == "visible"

    destroy_ctfd(app)


def test_can_delete_dynamic_challenge():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "dynamic"
        }

        r = client.post('/api/v1/challenges', json=challenge_data)
        assert r.get_json().get('data')['id'] == 1

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        DynamicValueChallenge.delete(challenge)

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 0
    destroy_ctfd(app)
