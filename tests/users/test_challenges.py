#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from freezegun import freeze_time

from CTFd.models import Challenges, Fails, Ratelimiteds, Solves
from CTFd.utils import set_config, text_type
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_fail,
    gen_flag,
    gen_hint,
    login_as_user,
    register_user,
)


def test_user_get_challenges():
    """
    Can a registered user load /challenges
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_chals():
    """
    Can a registered user load /chals
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_viewing_challenges():
    """
    Test that users can see added challenges
    """
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get("/api/v1/challenges")
        chals = r.get_json()["data"]
        assert len(chals) == 1
    destroy_ctfd(app)


def test_viewing_challenge():
    """Test that users can see individual challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get("/api/v1/challenges/1")
        assert r.get_json()
    destroy_ctfd(app)


# def test_chals_solves():
#     """Test that the /chals/solves endpoint works properly"""
#     app = create_ctfd()
#     with app.app_context():
#         # Generate 5 users
#         for c in range(1, 6):
#             name = "user{}".format(c)
#             email = "user{}@examplectf.com".format(c)
#             register_user(app, name=name, email=email, password="password")
#
#         # Generate 5 challenges
#         for c in range(6):
#             chal1 = gen_challenge(app.db, value=100)
#
#         user_ids = list(range(2, 7))
#         chal_ids = list(range(1, 6))
#         for u in user_ids:
#             for c in chal_ids:
#                 gen_solve(app.db, teamid=u, chalid=c)
#             chal_ids.pop()
#
#         client = login_as_user(app, name="user1")
#
#         with client.session_transaction() as sess:
#             r = client.get('/chals/solves')
#             output = r.get_data(as_text=True)
#             saved = json.loads('''{
#               "1": 5,
#               "2": 4,
#               "3": 3,
#               "4": 2,
#               "5": 1,
#               "6": 0
#             }
#             ''')
#             received = json.loads(output)
#             assert saved == received
#         set_config('hide_scores', True)
#         with client.session_transaction():
#             r = client.get('/chals/solves')
#             output = r.get_data(as_text=True)
#             saved = json.loads('''{
#               "1": -1,
#               "2": -1,
#               "3": -1,
#               "4": -1,
#               "5": -1,
#               "6": -1
#             }
#             ''')
#             received = json.loads(output)
#             assert saved == received
#     destroy_ctfd(app)


def test_submitting_correct_flag():
    """Test that correct flags are correct"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        data = {"submission": "flag", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "correct"
        assert resp.get("message") == "Correct"
    destroy_ctfd(app)


def test_submitting_correct_static_case_insensitive_flag():
    """Test that correct static flags are correct if the static flag is marked case_insensitive"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal.id, content="flag", data="case_insensitive")
        data = {"submission": "FLAG", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "correct"
        assert resp.get("message") == "Correct"
    destroy_ctfd(app)


def test_submitting_correct_regex_case_insensitive_flag():
    """Test that correct regex flags are correct if the regex flag is marked case_insensitive"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(
            app.db,
            challenge_id=chal.id,
            type="regex",
            content="flag",
            data="case_insensitive",
        )
        data = {"submission": "FLAG", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "correct"
        assert resp.get("message") == "Correct"
    destroy_ctfd(app)


def test_submitting_invalid_regex_flag():
    """Test that invalid regex flags are errored out to the user"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(
            app.db,
            challenge_id=chal.id,
            type="regex",
            content="**",
            data="case_insensitive",
        )
        data = {"submission": "FLAG", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "incorrect"
        assert resp.get("message") == "Regex parse error occured"
    destroy_ctfd(app)


def test_submitting_incorrect_flag():
    """Test that incorrect flags are incorrect"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        data = {"submission": "notflag", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "incorrect"
        assert resp.get("message") == "Incorrect"
    destroy_ctfd(app)


def test_submitting_unicode_flag():
    """Test that users can submit a unicode flag"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal.id, content="你好")
        with client.session_transaction():
            data = {"submission": "你好", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "correct"
        assert resp.get("message") == "Correct"
    destroy_ctfd(app)


def test_challenges_with_max_attempts():
    """Test that users are locked out of a challenge after they reach max_attempts"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal = Challenges.query.filter_by(id=chal.id).first()
        chal_id = chal.id
        chal.max_attempts = 3
        app.db.session.commit()

        gen_flag(app.db, challenge_id=chal.id, content="flag")
        for _ in range(3):
            data = {"submission": "notflag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)

        wrong_keys = Fails.query.count()
        assert wrong_keys == 3

        data = {"submission": "flag", "challenge_id": chal_id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403

        resp = r.get_json()["data"]
        assert resp.get("status") == "ratelimited"
        assert resp.get("message") == "Not accepted. You have 0 tries remaining"

        solves = Solves.query.count()
        assert solves == 0
    destroy_ctfd(app)


def test_challenges_with_max_attempts_timeout_behavior():
    """Test that users are temporarily locked out of a challenge after reaching max_attempts with timeout behavior"""

    app = create_ctfd()
    with app.app_context():
        set_config("max_attempts_behavior", "timeout")
        set_config("max_attempts_timeout", 300)  # 300 seconds timeout for test

        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal = Challenges.query.filter_by(id=chal.id).first()
        chal_id = chal.id
        chal.max_attempts = 2
        app.db.session.commit()

        gen_flag(app.db, challenge_id=chal.id, content="flag")
        for _ in range(2):
            data = {"submission": "notflag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200

        # Should be locked out now
        with freeze_time(timedelta(seconds=0)):
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429
            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert "Not accepted. Try again in 300 seconds" in resp.get("message")

        # Use freeze_time to advance time by 290 seconds
        with freeze_time(timedelta(seconds=290)):
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429
            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert "Not accepted. Try again in 10 seconds" in resp.get("message")

        # Use freeze_time to advance time by 301 seconds
        with freeze_time(timedelta(seconds=301)):
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            resp = r.get_json()["data"]
            # Should be correct now
            assert resp.get("status") == "correct"
            assert resp.get("message") == "Correct"
    destroy_ctfd(app)


def test_challenges_with_max_attempts_timeout_ratelimit():
    """Test that max_attempts timeout ratelimit and global ratelimit work together correctly"""
    app = create_ctfd()
    with app.app_context():
        set_config("max_attempts_behavior", "timeout")
        set_config("max_attempts_timeout", 30)  # 30 seconds timeout for test

        register_user(app)
        client = login_as_user(app)

        # Challenge 1 with max_attempts = 5
        chal1 = gen_challenge(app.db)
        chal1_obj = Challenges.query.filter_by(id=chal1.id).first()
        chal1_obj.max_attempts = 5
        app.db.session.commit()
        gen_flag(app.db, challenge_id=chal1.id, content="flag1")

        # Challenge 2 with no max_attempts
        chal2 = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal2.id, content="flag2")

        base_time = datetime.utcnow()

        # Submit 5 wrong attempts to challenge 1 (triggers max_attempts ratelimit)
        with freeze_time(base_time):
            for _ in range(5):
                data = {"submission": "wrong", "challenge_id": chal1.id}
                r = client.post("/api/v1/challenges/attempt", json=data)
                assert r.status_code == 200

            # 6th attempt should be blocked by max_attempts timeout
            data = {"submission": "flag1", "challenge_id": chal1.id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429
            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert "Try again in 30 seconds" in resp.get("message")

            # Now submit 5 more wrong attempts to challenge 2 (total 10 fails, triggers global ratelimit)
            for i in range(6):
                data = {"submission": "wrong", "challenge_id": chal2.id}
                r = client.post("/api/v1/challenges/attempt", json=data)
                if i < 5:
                    assert r.status_code == 200
                else:
                    # 11th attempt should be blocked by global ratelimit (60 seconds)
                    assert r.status_code == 429
                    resp = r.get_json()["data"]
                    assert resp.get("status") == "ratelimited"
                    assert "You're submitting flags too fast" in resp.get("message")

            # Check counts
            wrong_keys = Fails.query.count()
            ratelimiteds = Ratelimiteds.query.count()
            assert wrong_keys == 10
            assert (
                ratelimiteds == 2
            )  # One max_attempts ratelimit + one global ratelimit

        # After 30 seconds, max_attempts timeout should release but global ratelimit (60s) still active
        with freeze_time(base_time + timedelta(seconds=31)):
            # Try challenge 1 - should still be blocked by global ratelimit
            data = {"submission": "flag1", "challenge_id": chal1.id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429
            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert "Try again in 30 seconds" in resp.get("message")

            ratelimiteds = Ratelimiteds.query.count()
            assert ratelimiteds == 3  # Another ratelimit entry

        # After 60 seconds, both ratelimits should be released
        with freeze_time(base_time + timedelta(seconds=61)):
            # Should be able to solve challenge 1 now
            data = {"submission": "flag1", "challenge_id": chal1.id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            resp = r.get_json()["data"]
            assert resp.get("status") == "correct"
            assert resp.get("message") == "Correct"

            # Verify solve was recorded
            solves = Solves.query.count()
            assert solves == 1
    destroy_ctfd(app)


def test_challenges_max_attempts_timeout_config_change():
    """Test that changing max_attempts_timeout resets attempt count because cache key changes"""
    app = create_ctfd()
    with app.app_context():
        set_config("max_attempts_behavior", "timeout")
        set_config("max_attempts_timeout", 300)  # Start with 300 seconds

        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal = Challenges.query.filter_by(id=chal.id).first()
        chal_id = chal.id
        chal.max_attempts = 3
        app.db.session.commit()

        gen_flag(app.db, challenge_id=chal.id, content="flag")

        # Make 3 wrong attempts (hit the limit)
        for _ in range(3):
            data = {"submission": "notflag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200

        # Verify we're locked out
        data = {"submission": "flag", "challenge_id": chal_id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 429
        resp = r.get_json()["data"]
        assert resp.get("status") == "ratelimited"
        assert "300 seconds" in resp.get("message")

        # Change the max_attempts_timeout config (this changes the cache key)
        set_config("max_attempts_timeout", 30)  # Change to 30 seconds

        # Jump forward in time to ensure we're past the new 30 second rate limit
        with freeze_time(timedelta(seconds=35)):
            # Now we should be able to submit again because the cache key changed
            # Old submissions have also fallen off the 30 second window
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            resp = r.get_json()["data"]
            assert resp.get("status") == "correct"
            assert resp.get("message") == "Correct"

        # Verify solve was recorded
        solves = Solves.query.count()
        assert solves == 1

        # Verify the fail count is still accurate (3 fails from before)
        fails = Fails.query.count()
        assert fails == 3

        ratelimiteds = Ratelimiteds.query.count()
        assert ratelimiteds == 1
    destroy_ctfd(app)


def test_challenge_kpm_limit_no_freeze():
    """Test that users are properly ratelimited when submitting flags"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id

        gen_flag(app.db, challenge_id=chal.id, content="flag")
        for _ in range(11):
            with client.session_transaction():
                data = {"submission": "notflag", "challenge_id": chal_id}
            client.post("/api/v1/challenges/attempt", json=data)

        wrong_keys = Fails.query.count()
        ratelimiteds = Ratelimiteds.query.count()
        assert wrong_keys == 10
        assert ratelimiteds == 1

        # We just want a consistent flag response countdown
        with freeze_time(timedelta(seconds=0)):
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429

            wrong_keys = Fails.query.count()
            ratelimiteds = Ratelimiteds.query.count()
            assert wrong_keys == 10
            assert ratelimiteds == 2

            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert (
                resp.get("message")
                == "You're submitting flags too fast. Try again in 60 seconds."
            )

        solves = Solves.query.count()
        assert solves == 0
    destroy_ctfd(app)


def test_challenge_kpm_limit_freeze_time():
    """Test that users are properly ratelimited when submitting flags"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id

        gen_flag(app.db, challenge_id=chal.id, content="flag")
        base_time = datetime.utcnow()

        # First section: Use API to generate 10 fails + 1 ratelimit
        with freeze_time(base_time):
            for _ in range(11):
                with client.session_transaction():
                    data = {"submission": "notflag", "challenge_id": chal_id}
                r = client.post("/api/v1/challenges/attempt", json=data)

            wrong_keys = Fails.query.count()
            ratelimiteds = Ratelimiteds.query.count()
            assert wrong_keys == 10
            assert ratelimiteds == 1

        # Within the 1 min time frame we should still be ratelimited
        with freeze_time(base_time + timedelta(seconds=11)):
            data = {"submission": "flag", "challenge_id": chal_id}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 429

            wrong_keys = Fails.query.count()
            ratelimiteds = Ratelimiteds.query.count()
            assert wrong_keys == 10
            assert ratelimiteds == 2

            resp = r.get_json()["data"]
            assert resp.get("status") == "ratelimited"
            assert (
                resp.get("message")
                == "You're submitting flags too fast. Try again in 50 seconds."
            )

        # Generate 10 more fails at +60 seconds using gen_fail because freezegun cannot patch to sqlalchemy's default
        for _ in range(10):
            fail = gen_fail(app.db, user_id=2, challenge_id=chal_id, provided="notflag")
            fail.date = base_time + timedelta(seconds=60)
            app.db.session.commit()

        # The 11th attempt via API should trigger another ratelimit
        with freeze_time(base_time + timedelta(seconds=60)):
            data = {"submission": "notflag", "challenge_id": chal_id}
            client.post("/api/v1/challenges/attempt", json=data)

            wrong_keys = Fails.query.count()
            ratelimiteds = Ratelimiteds.query.count()
            assert wrong_keys == 20
            assert ratelimiteds == 3
    destroy_ctfd(app)


def test_that_view_challenges_unregistered_works():
    """Test that view_challenges_unregistered works"""
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db, name=text_type("🐺"))
        chal_id = chal.id
        gen_hint(app.db, chal_id)

        client = app.test_client()
        r = client.get("/api/v1/challenges", json="")
        assert r.status_code == 403
        r = client.get("/api/v1/challenges")
        assert r.status_code == 302

        set_config("challenge_visibility", "public")

        client = app.test_client()
        r = client.get("/api/v1/challenges")
        assert r.get_json()["data"]

        r = client.get("/api/v1/challenges/1/solves")
        assert r.get_json().get("data") is not None

        data = {"submission": "not_flag", "challenge_id": chal_id}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403
        assert r.get_json().get("data").get("status") == "authentication_required"
        assert r.get_json().get("data").get("message") is None
    destroy_ctfd(app)


def test_hidden_challenge_is_unreachable():
    """Test that hidden challenges return 404 and do not insert a solve or wrong key"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db, state="hidden")
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        chal_id = chal.id

        assert Challenges.query.count() == 1

        r = client.get("/api/v1/challenges", json="")
        data = r.get_json().get("data")
        assert data == []

        r = client.get("/api/v1/challenges/1", json="")
        assert r.status_code == 404
        data = r.get_json().get("data")
        assert data is None

        data = {"submission": "flag", "challenge_id": chal_id}

        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 404

        r = client.post("/api/v1/challenges/attempt?preview=true", json=data)
        assert r.status_code == 404
        assert r.get_json().get("data") is None

        solves = Solves.query.count()
        assert solves == 0

        wrong_keys = Fails.query.count()
        assert wrong_keys == 0
    destroy_ctfd(app)


def test_hidden_challenge_is_unsolveable():
    """Test that hidden challenges return 404 and do not insert a solve or wrong key"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db, state="hidden")
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        data = {"submission": "flag", "challenge_id": chal.id}

        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 404

        solves = Solves.query.count()
        assert solves == 0

        wrong_keys = Fails.query.count()
        assert wrong_keys == 0
    destroy_ctfd(app)


def test_invalid_requirements_are_rejected():
    """Test that invalid requirements JSON blobs are rejected by the API"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            # Test None/null values
            r = client.patch(
                "/api/v1/challenges/1", json={"requirements": {"prerequisites": [None]}}
            )
            assert r.status_code == 400
            assert r.get_json() == {
                "success": False,
                "errors": {
                    "requirements": [
                        "Challenge requirements cannot have a null prerequisite"
                    ]
                },
            }
            # Test empty strings
            r = client.patch(
                "/api/v1/challenges/1", json={"requirements": {"prerequisites": [""]}}
            )
            assert r.status_code == 400
            assert r.get_json() == {
                "success": False,
                "errors": {
                    "requirements": [
                        "Challenge requirements cannot have a null prerequisite"
                    ]
                },
            }
            # Test a valid integer
            r = client.patch(
                "/api/v1/challenges/1", json={"requirements": {"prerequisites": [2]}}
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_challenge_with_requirements_is_unsolveable():
    """Test that a challenge with a requirement is unsolveable without first solving the requirement"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal1 = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal1.id, content="flag")

        requirements = {"prerequisites": [1]}
        chal2 = gen_challenge(app.db, requirements=requirements)
        app.db.session.commit()

        gen_flag(app.db, challenge_id=chal2.id, content="flag")

        r = client.get("/api/v1/challenges")
        challenges = r.get_json()["data"]
        assert len(challenges) == 1
        assert challenges[0]["id"] == 1

        r = client.get("/api/v1/challenges/2")
        assert r.status_code == 403
        assert r.get_json().get("data") is None

        # Attempt to solve hidden Challenge 2
        data = {"submission": "flag", "challenge_id": 2}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403
        assert r.get_json().get("data") is None

        # Solve Challenge 1
        data = {"submission": "flag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        resp = r.get_json()["data"]
        assert resp["status"] == "correct"

        # Challenge 2 should now be visible
        r = client.get("/api/v1/challenges")
        challenges = r.get_json()["data"]
        assert len(challenges) == 2

        r = client.get("/api/v1/challenges/2")
        assert r.status_code == 200
        assert r.get_json().get("data")["id"] == 2

        # Attempt to solve the now-visible Challenge 2
        data = {"submission": "flag", "challenge_id": 2}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        assert resp["status"] == "correct"

    destroy_ctfd(app)


def test_challenges_cannot_be_solved_while_paused():
    """Test that challenges cannot be solved when the CTF is paused"""
    app = create_ctfd()
    with app.app_context():
        set_config("paused", True)

        register_user(app)
        client = login_as_user(app)

        r = client.get("/challenges")
        assert r.status_code == 200

        # Assert that there is a paused message
        data = r.get_data(as_text=True)
        assert "paused" in data

        chal = gen_challenge(app.db)
        gen_flag(app.db, challenge_id=chal.id, content="flag")

        data = {"submission": "flag", "challenge_id": chal.id}
        r = client.post("/api/v1/challenges/attempt", json=data)

        # Assert that the JSON message is correct
        resp = r.get_json()["data"]
        assert r.status_code == 403
        assert resp["status"] == "paused"
        assert resp["message"] == "CTFd is paused"

        # There are no solves saved
        solves = Solves.query.count()
        assert solves == 0

        # There are no wrong keys saved
        wrong_keys = Fails.query.count()
        assert wrong_keys == 0
    destroy_ctfd(app)


def test_challenge_board_under_view_after_ctf():
    """Test that the challenge board does not show an error under view_after_ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config("view_after_ctf", True)
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        register_user(app)
        client = login_as_user(app)

        gen_challenge(app.db)
        gen_flag(app.db, challenge_id=1, content="flag")

        gen_challenge(app.db)
        gen_flag(app.db, challenge_id=2, content="flag")

        # CTF hasn't started yet. There should be an error message.
        with freeze_time("2017-10-3"):
            r = client.get("/challenges")
            assert r.status_code == 403
            assert "has not started yet" in r.get_data(as_text=True)

            data = {"submission": "flag", "challenge_id": 2}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 403
            assert Solves.query.count() == 0

        # CTF is ongoing. Normal operation.
        with freeze_time("2017-10-5"):
            r = client.get("/challenges")
            assert r.status_code == 200
            assert "has ended" not in r.get_data(as_text=True)

            data = {"submission": "flag", "challenge_id": 1}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
            assert Solves.query.count() == 1

        # CTF is now over. There should be a message and challenges should show submission status but not store solves
        with freeze_time("2017-10-7"):
            r = client.get("/challenges")
            assert r.status_code == 200
            assert "has ended" in r.get_data(as_text=True)

            data = {"submission": "flag", "challenge_id": 2}
            r = client.post("/api/v1/challenges/attempt", json=data)
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
            assert Solves.query.count() == 1
    destroy_ctfd(app)


def test_challenges_under_view_after_ctf():
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

        gen_challenge(app.db)
        gen_flag(app.db, challenge_id=1, content="flag")

        r = client.get("/challenges")
        assert r.status_code == 403

        r = client.get("/api/v1/challenges")
        assert r.status_code == 403
        assert r.get_json().get("data") is None

        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 403
        assert r.get_json().get("data") is None

        data = {"submission": "flag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403
        assert r.get_json().get("data") is None
        assert Solves.query.count() == 0

        data = {"submission": "notflag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403
        assert r.get_json().get("data") is None
        assert Fails.query.count() == 0

        set_config("view_after_ctf", True)

        r = client.get("/challenges")
        assert r.status_code == 200

        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        assert r.get_json()["data"][0]["id"] == 1

        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        assert r.get_json()["data"]["id"] == 1

        data = {"submission": "flag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        assert r.get_json()["data"]["status"] == "correct"
        assert Solves.query.count() == 0

        data = {"submission": "notflag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
        assert r.get_json()["data"]["status"] == "incorrect"
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_challenges_admin_only_as_user():
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "admins")

        register_user(app)
        admin = login_as_user(app, name="admin")

        gen_challenge(app.db)
        gen_flag(app.db, challenge_id=1, content="flag")

        r = admin.get("/challenges")
        assert r.status_code == 200

        r = admin.get("/api/v1/challenges", json="")
        assert r.status_code == 200

        r = admin.get("/api/v1/challenges/1", json="")
        assert r.status_code == 200

        data = {"submission": "flag", "challenge_id": 1}
        r = admin.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 200
    destroy_ctfd(app)
