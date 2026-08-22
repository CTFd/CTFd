#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Challenges
from CTFd.plugins.challenges import CTFdStandardChallenge
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


def test_can_create_standard_dynamic_challenge():
    """Test that standard dynamic challenges can be made from the API/admin panel"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "function": "linear",
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        challenges = Challenges.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        assert challenge.value == 100
        assert challenge.initial == 100
        assert challenge.decay == 20
        assert challenge.minimum == 1
        assert challenge.function == "linear"
    destroy_ctfd(app)


def test_can_update_standard_dynamic_challenge():
    app = create_ctfd()
    with app.app_context():
        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "hidden",
            "type": "standard",
        }
        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.create(req)

        assert challenge.value == 100
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None
        assert challenge.function == "static"

        challenge_data = {
            "name": "new_name",
            "category": "category",
            "description": "new_description",
            "value": "200",
            "function": "linear",
            "initial": "200",
            "decay": "40",
            "minimum": "5",
            "max_attempts": "0",
            "state": "visible",
        }

        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.update(challenge, req)

        assert challenge.name == "new_name"
        assert challenge.description == "new_description"
        assert challenge.value == 200
        assert challenge.initial == 200
        assert challenge.decay == 40
        assert challenge.minimum == 5
        assert challenge.function == "linear"
        assert challenge.state == "visible"

    destroy_ctfd(app)


def test_can_add_requirement_standard_dynamic_challenge():
    """Test that requirements can be added to dynamic challenges"""
    app = create_ctfd()
    with app.app_context():
        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "function": "linear",
            "value": 100,
            "decay": 20,
            "minimum": 1,
            "state": "hidden",
            "type": "standard",
        }
        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.create(req)

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
            "function": "logarithmic",
            "max_attempts": "0",
            "state": "visible",
        }

        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.create(req)

        assert challenge.name == "second_name"
        assert challenge.description == "new_description"
        assert challenge.function == "logarithmic"
        assert challenge.value == 200
        assert challenge.initial == 200
        assert challenge.decay == 40
        assert challenge.minimum == 5
        assert challenge.state == "visible"

        challenge_data = {"requirements": [1]}

        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.update(challenge, req)

        assert challenge.requirements == [1]

    destroy_ctfd(app)


def test_can_delete_standard_dynamic_challenge():
    """Test that dynamic challenges can be deleted"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "function": "linear",
            "state": "hidden",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        challenges = Challenges.query.all()
        assert len(challenges) == 1

        challenge = challenges[0]
        CTFdStandardChallenge.delete(challenge)

        challenges = Challenges.query.all()
        assert len(challenges) == 0
    destroy_ctfd(app)


def test_standard_dynamic_challenge_loses_value_properly():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "function": "logarithmic",
            "state": "visible",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        gen_flag(app.db, challenge_id=1, content="flag")

        for i, team_id in enumerate(range(2, 26)):
            name = "user{}".format(team_id)
            email = "user{}@examplectf.com".format(team_id)
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

                chal = Challenges.query.filter_by(id=1).first()
                if i >= 20:
                    assert chal.value == chal.minimum
                else:
                    assert chal.initial >= chal.value
                    assert chal.value > chal.minimum
    destroy_ctfd(app)


def test_standard_dynamic_challenge_doesnt_lose_value_on_update():
    """Standard Dynamic challenge updates without changing any values or solves shouldn't change the current value. See #1043"""
    app = create_ctfd()
    with app.app_context():
        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 10000,
            "initial": 10000,
            "decay": 4,
            "minimum": 10,
            "function": "logarithmic",
            "state": "visible",
            "type": "standard",
        }
        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.create(req)
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
        chal = CTFdStandardChallenge.update(chal, req)
        assert prev_chal_value == chal.value
    destroy_ctfd(app)


def test_standard_dynamic_challenge_value_isnt_affected_by_hidden_users():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "function": "logarithmic",
            "state": "visible",
            "type": "standard",
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
        for _, team_id in enumerate(range(2, 26)):
            name = "user{}".format(team_id)
            email = "user{}@examplectf.com".format(team_id)
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

                chal = Challenges.query.filter_by(id=1).first()
                assert chal.value == chal.initial
    destroy_ctfd(app)


def test_standard_dynamic_challenges_reset():
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "initial": 100,
            "decay": 20,
            "minimum": 1,
            "function": "linear",
            "state": "hidden",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert Challenges.query.count() == 1

        with client.session_transaction() as sess:
            data = {"nonce": sess.get("nonce"), "challenges": "on"}
            r = client.post("/admin/reset", data=data)
            assert r.location.endswith("/admin/statistics")
        assert Challenges.query.count() == 0

    destroy_ctfd(app)


def test_standard_dynamic_challenge_linear_loses_value_properly():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "function": "linear",
            "value": 100,
            "initial": 100,
            "decay": 5,
            "minimum": 1,
            "state": "visible",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        gen_flag(app.db, challenge_id=1, content="flag")

        for i, team_id in enumerate(range(2, 26)):
            name = "user{}".format(team_id)
            email = "user{}@examplectf.com".format(team_id)
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

                chal = Challenges.query.filter_by(id=1).first()

                if i >= 20:
                    assert chal.value == chal.minimum
                else:
                    assert chal.value == (chal.initial - (i * 5))
    destroy_ctfd(app)


def test_standard_challenges_default_to_static_function():
    """Test that standard challenges by default are created with static function"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        # Test creating challenge without specifying function - should default to static
        challenge_data = {
            "name": "default_challenge",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "visible",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1

        challenge = Challenges.query.filter_by(id=1).first()

        # Assert that function defaults to "static"
        assert challenge.function == "static"
        assert challenge.value == 100
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None

        # Test with direct model creation (via CTFdStandardChallenge.create)
        challenge_data2 = {
            "name": "direct_challenge",
            "category": "category",
            "description": "description",
            "value": 200,
            "state": "visible",
            "type": "standard",
            # Note: no function specified
        }

        req = FakeRequest(form=challenge_data2)
        challenge2 = CTFdStandardChallenge.create(req)

        # Assert that function defaults to "static"
        assert challenge2.function == "static"
        assert challenge2.value == 200
        assert challenge2.initial is None
        assert challenge2.decay is None
        assert challenge2.minimum is None

        # Test that static challenges maintain their value after solves
        gen_flag(app.db, challenge_id=challenge2.id, content="flag")

        # Create a user and solve the challenge
        user = gen_user(app.db, name="solver", email="solver@example.com")
        with app.test_client() as test_client:
            with test_client.session_transaction() as sess:
                sess["id"] = user.id
                sess["nonce"] = "fake-nonce"
                sess["hash"] = hmac(user.password)

            data = {"submission": "flag", "challenge_id": challenge2.id}
            r = test_client.post("/api/v1/challenges/attempt", json=data)
            resp = r.get_json()["data"]
            assert resp["status"] == "correct"

            # Challenge value should remain unchanged for static challenges
            challenge2_after = Challenges.query.filter_by(id=challenge2.id).first()
            assert challenge2_after.value == 200
            assert challenge2_after.function == "static"

    destroy_ctfd(app)


def test_standard_dynamic_challenge_update_overrides_manual_value():
    """Test that updating a dynamic challenge recalculates value even when a manual value is provided"""
    app = create_ctfd()
    with app.app_context():
        # Create initial dynamic challenge
        challenge_data = {
            "name": "dynamic_challenge",
            "category": "category",
            "description": "description",
            "function": "linear",
            "initial": 100,
            "decay": 10,
            "minimum": 10,
            "state": "visible",
            "type": "standard",
        }
        req = FakeRequest(form=challenge_data)
        challenge = CTFdStandardChallenge.create(req)
        challenge_id = challenge.id

        # Verify initial state
        assert challenge.function == "linear"
        assert challenge.value == 100  # Should match initial value
        assert challenge.initial == 100
        assert challenge.decay == 10
        assert challenge.minimum == 10

        # Add a flag and create some solves to change the dynamic value
        gen_flag(app.db, challenge_id=challenge_id, content="flag")

        # Create some users and solves to trigger value decay
        for i in range(3):
            user = gen_user(app.db, name=f"user{i}", email=f"user{i}@example.com")
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess["id"] = user.id
                    sess["nonce"] = "fake-nonce"
                    sess["hash"] = hmac(user.password)

                data = {"submission": "flag", "challenge_id": challenge_id}
                r = client.post("/api/v1/challenges/attempt", json=data)
                assert r.get_json()["data"]["status"] == "correct"

        # Check that value has decreased due to linear decay
        challenge_after_solves = Challenges.query.filter_by(id=challenge_id).first()
        # Linear formula: initial - (decay * solve_count), with solve_count adjusted by -1
        # So with 3 solves: 100 - (10 * 2) = 80
        expected_value_after_solves = 80
        assert challenge_after_solves.value == expected_value_after_solves

        # Now update the challenge with a manual override value but keep same parameters
        update_data = {
            "name": "updated_dynamic_challenge",
            "description": "updated description",
            "value": 100,  # This should be ignored since it's a dynamic challenge and value should be calculated on the fly
            "function": "linear",
            "initial": 100,  # Keep same initial value
            "decay": 10,  # Keep same decay value
            "minimum": 10,  # Keep same minimum value
        }

        req = FakeRequest(form=update_data)
        updated_challenge = CTFdStandardChallenge.update(challenge_after_solves, req)

        # Verify that the manual value (100) was ignored and dynamic calculation maintained current value
        # Since parameters didn't change and we have 3 solves, value should remain 80
        assert (
            updated_challenge.value == 80
        )  # Should stay at dynamically calculated value, not the sent value of 100
        assert updated_challenge.initial == 100  # Parameters should remain the same
        assert updated_challenge.decay == 10
        assert updated_challenge.minimum == 10
        assert updated_challenge.function == "linear"

        # The name and description should be updated
        assert updated_challenge.name == "updated_dynamic_challenge"
        assert updated_challenge.description == "updated description"

        # Test that subsequent solves continue to use the same parameters correctly
        user4 = gen_user(app.db, name="user4", email="user4@example.com")
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["id"] = user4.id
                sess["nonce"] = "fake-nonce"
                sess["hash"] = hmac(user4.password)

            data = {"submission": "flag", "challenge_id": challenge_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.get_json()["data"]["status"] == "correct"

        # After 4 total solves: 100 - (10 * 3) = 70
        final_challenge = Challenges.query.filter_by(id=challenge_id).first()
        expected_final_value = 70
        assert final_challenge.value == expected_final_value

    destroy_ctfd(app)


def test_standard_dynamic_challenge_creation_requires_all_parameters():
    """Test that creating a dynamic challenge without initial, minimum, and decay raises an error"""
    app = create_ctfd()
    with app.app_context():
        from CTFd.exceptions.challenges import ChallengeCreateException

        # Test missing initial parameter for linear function
        challenge_data_missing_initial = {
            "name": "missing_initial",
            "category": "category",
            "description": "description",
            "function": "linear",
            "decay": 10,
            "minimum": 5,
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=challenge_data_missing_initial)
        try:
            CTFdStandardChallenge.create(req)
            raise AssertionError(
                "Should have raised ChallengeCreateException for missing initial"
            )
        except ChallengeCreateException as e:
            assert "Missing 'initial'" in str(e)
            assert "function is linear" in str(e)

        # Test missing decay parameter for logarithmic function
        challenge_data_missing_decay = {
            "name": "missing_decay",
            "category": "category",
            "description": "description",
            "function": "logarithmic",
            "initial": 100,
            "minimum": 5,
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=challenge_data_missing_decay)
        try:
            CTFdStandardChallenge.create(req)
            raise AssertionError(
                "Should have raised ChallengeCreateException for missing decay"
            )
        except ChallengeCreateException as e:
            assert "Missing 'decay'" in str(e)
            assert "function is logarithmic" in str(e)

        # Test missing minimum parameter for linear function
        challenge_data_missing_minimum = {
            "name": "missing_minimum",
            "category": "category",
            "description": "description",
            "function": "linear",
            "initial": 100,
            "decay": 10,
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=challenge_data_missing_minimum)
        try:
            CTFdStandardChallenge.create(req)
            raise AssertionError(
                "Should have raised ChallengeCreateException for missing minimum"
            )
        except ChallengeCreateException as e:
            assert "Missing 'minimum'" in str(e)
            assert "function is linear" in str(e)

        # Test missing all dynamic parameters
        challenge_data_missing_all = {
            "name": "missing_all",
            "category": "category",
            "description": "description",
            "function": "logarithmic",
            "value": 100,  # Only static value provided
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=challenge_data_missing_all)
        try:
            CTFdStandardChallenge.create(req)
            raise AssertionError(
                "Should have raised ChallengeCreateException for missing all dynamic parameters"
            )
        except ChallengeCreateException as e:
            # Should catch the first missing parameter (likely 'initial')
            assert "Missing" in str(e)
            assert "function is logarithmic" in str(e)

        # Test that static challenges don't require dynamic parameters
        static_challenge_data = {
            "name": "static_challenge",
            "category": "category",
            "description": "description",
            "function": "static",
            "value": 100,
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=static_challenge_data)
        # This should NOT raise an exception
        static_challenge = CTFdStandardChallenge.create(req)
        assert static_challenge.function == "static"
        assert static_challenge.value == 100
        assert static_challenge.initial is None
        assert static_challenge.decay is None
        assert static_challenge.minimum is None

        # Test that providing all required parameters works
        valid_dynamic_challenge_data = {
            "name": "valid_dynamic",
            "category": "category",
            "description": "description",
            "function": "linear",
            "initial": 200,
            "decay": 15,
            "minimum": 10,
            "state": "visible",
            "type": "standard",
        }

        req = FakeRequest(form=valid_dynamic_challenge_data)
        # This should NOT raise an exception
        valid_challenge = CTFdStandardChallenge.create(req)
        assert valid_challenge.function == "linear"
        assert valid_challenge.value == 200
        assert valid_challenge.initial == 200
        assert valid_challenge.decay == 15
        assert valid_challenge.minimum == 10

    destroy_ctfd(app)


def test_dynamic_challenge_update_requires_all_parameters():
    """Test that updating a challenge to dynamic function without initial, minimum, and decay raises an error"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        # First create a static challenge via API
        initial_challenge_data = {
            "name": "static_challenge",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "visible",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=initial_challenge_data)
        assert r.status_code == 200
        challenge_id = r.get_json().get("data")["id"]

        # Verify it's initially static
        challenge = Challenges.query.get(1)
        assert challenge.function == "static"
        assert challenge.value == 100
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None

        # Test updating to linear function missing initial parameter
        update_data_missing_initial = {
            "function": "linear",
            "decay": 10,
            "minimum": 5,
        }

        r = client.patch(
            f"/api/v1/challenges/{challenge_id}", json=update_data_missing_initial
        )
        assert "Missing 'initial'" in r.get_json()["errors"][""][0]
        assert r.status_code == 500  # Should fail validation

        challenge = Challenges.query.get(challenge_id)
        assert challenge.function == "static"
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None

        # Test updating to logarithmic function missing decay parameter
        update_data_missing_decay = {
            "function": "logarithmic",
            "initial": 100,
            "minimum": 5,
        }

        r = client.patch(
            f"/api/v1/challenges/{challenge_id}", json=update_data_missing_decay
        )
        assert "Missing 'decay'" in r.get_json()["errors"][""][0]
        assert r.status_code == 500  # Should fail validation

        challenge = Challenges.query.get(challenge_id)
        assert challenge.function == "static"
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None

        # Test updating to logarithmic function missing minimum parameter
        update_data_missing_minimum = {
            "function": "logarithmic",
            "initial": 100,
            "decay": 10,
        }

        r = client.patch(
            f"/api/v1/challenges/{challenge_id}", json=update_data_missing_minimum
        )
        assert "Missing 'minimum'" in r.get_json()["errors"][""][0]
        assert r.status_code == 500  # Should fail validation

        challenge = Challenges.query.get(challenge_id)
        assert challenge.function == "static"
        assert challenge.initial is None
        assert challenge.decay is None
        assert challenge.minimum is None

        # Test that updating with all valid parameters works
        valid_update_data = {
            "function": "linear",
            "initial": 200,
            "decay": 15,
            "minimum": 10,
        }

        r = client.patch(f"/api/v1/challenges/{challenge_id}", json=valid_update_data)
        assert r.status_code == 200

        # Verify the challenge was updated correctly
        challenge = Challenges.query.get(challenge_id)
        assert challenge.function == "linear"
        assert challenge.initial == 200
        assert challenge.decay == 15
        assert challenge.minimum == 10

    destroy_ctfd(app)
