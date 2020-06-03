#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Challenges
from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge
from CTFd.utils.security.signing import hmac
from tests.helpers import (
    FakeRequest,
    create_ctfd,
    destroy_ctfd,
    gen_flag,
    gen_user,
    login_as_user,
    register_user,
)


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
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        assert challenge.value == 100
        assert challenge.initial == 100
        assert challenge.decay == 20
        assert challenge.minimum == 1
    destroy_ctfd(app)


def test_can_update_dynamic_challenge():
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
            "type": "dynamic",
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
            "state": "visible",
        }

        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.update(challenge, req)

        assert challenge.name == "new_name"
        assert challenge.description == "new_description"
        assert challenge.value == 200
        assert challenge.initial == 200
        assert challenge.decay == 40
        assert challenge.minimum == 5
        assert challenge.state == "visible"

    destroy_ctfd(app)


def test_can_add_requirement_dynamic_challenge():
    """Test that requirements can be added to dynamic challenges"""
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
            "type": "dynamic",
        }
        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.create(req)

        assert challenge.value == 100
        assert challenge.initial == 100
        assert challenge.decay == 20
        assert challenge.minimum == 1

        challenge_data = {
            "name": "second_name",
            "category": "category",
            "description": "new_description",
            "value": "200",
            "initial": "200",
            "decay": "40",
            "minimum": "5",
            "max_attempts": "0",
            "state": "visible",
        }

        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.create(req)

        assert challenge.name == "second_name"
        assert challenge.description == "new_description"
        assert challenge.value == 200
        assert challenge.initial == 200
        assert challenge.decay == 40
        assert challenge.minimum == 5
        assert challenge.state == "visible"

        challenge_data = {"requirements": [1]}

        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.update(challenge, req)

        assert challenge.requirements == [1]

    destroy_ctfd(app)


def test_can_delete_dynamic_challenge():
    """Test that dynamic challenges can be deleted"""
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
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        DynamicValueChallenge.delete(challenge)

        challenges = DynamicChallenge.query.all()
        assert len(challenges) == 0
    destroy_ctfd(app)


def test_dynamic_challenge_loses_value_properly():
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
            "state": "visible",
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        gen_flag(app.db, challenge_id=1, content="flag")

        for i, team_id in enumerate(range(2, 26)):
            name = "user{}".format(team_id)
            email = "user{}@ctfd.io".format(team_id)
            # We need to bypass rate-limiting so gen_user instead of register_user
            user = gen_user(app.db, name=name, email=email)
            user_id = user.id

            with app.test_client() as client:
                # We need to bypass rate-limiting so creating a fake user instead of logging in
                with client.session_transaction() as sess:
                    sess["id"] = user_id
                    sess["nonce"] = "fake-nonce"
                    sess["hash"] = hmac(user.password)

                data = {"submission": "flag", "challenge_id": 1}

                r = client.post("/api/v1/challenges/attempt", json=data)
                resp = r.get_json()["data"]
                assert resp["status"] == "correct"

                chal = DynamicChallenge.query.filter_by(id=1).first()
                if i >= 20:
                    assert chal.value == chal.minimum
                else:
                    assert chal.initial >= chal.value
                    assert chal.value > chal.minimum
    destroy_ctfd(app)


def test_dynamic_challenge_doesnt_lose_value_on_update():
    """Dynamic challenge updates without changing any values or solves shouldn't change the current value. See #1043"""
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 10000,
            "decay": 4,
            "minimum": 10,
            "state": "visible",
            "type": "dynamic",
        }
        req = FakeRequest(form=challenge_data)
        challenge = DynamicValueChallenge.create(req)
        challenge_id = challenge.id
        gen_flag(app.db, challenge_id=challenge.id, content="flag")
        register_user(app)
        with login_as_user(app) as client:
            data = {"submission": "flag", "challenge_id": challenge_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
        chal = Challenges.query.filter_by(id=challenge_id).first()
        prev_chal_value = chal.value
        chal = DynamicValueChallenge.update(chal, req)
        assert prev_chal_value == chal.value
    destroy_ctfd(app)


def test_dynamic_challenge_value_isnt_affected_by_hidden_users():
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
            "state": "visible",
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        gen_flag(app.db, challenge_id=1, content="flag")

        # Make a solve as a regular user. This should not affect the value.
        data = {"submission": "flag", "challenge_id": 1}

        r = client.post("/api/v1/challenges/attempt", json=data)
        resp = r.get_json()["data"]
        assert resp["status"] == "correct"

        # Make solves as hidden users. Also should not affect value
        for i, team_id in enumerate(range(2, 26)):
            name = "user{}".format(team_id)
            email = "user{}@ctfd.io".format(team_id)
            # We need to bypass rate-limiting so gen_user instead of register_user
            user = gen_user(app.db, name=name, email=email)
            user.hidden = True
            app.db.session.commit()
            user_id = user.id

            with app.test_client() as client:
                # We need to bypass rate-limiting so creating a fake user instead of logging in
                with client.session_transaction() as sess:
                    sess["id"] = user_id
                    sess["nonce"] = "fake-nonce"
                    sess["hash"] = hmac(user.password)

                data = {"submission": "flag", "challenge_id": 1}

                r = client.post("/api/v1/challenges/attempt", json=data)
                assert r.status_code == 200
                resp = r.get_json()["data"]
                assert resp["status"] == "correct"

                chal = DynamicChallenge.query.filter_by(id=1).first()
                assert chal.value == chal.initial
    destroy_ctfd(app)


def test_dynamic_challenges_reset():
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "dynamic",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert Challenges.query.count() == 1
        assert DynamicChallenge.query.count() == 1

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "challenges": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Challenges.query.count() == 0
        assert DynamicChallenge.query.count() == 0

    destroy_ctfd(app)
