#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import mock

from freezegun import freeze_time

from CTFd.models import Challenges, Flags, Hints, Solves, Tags, Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_fail,
    gen_flag,
    gen_hint,
    gen_solve,
    gen_tag,
    gen_team,
    gen_topic,
    gen_user,
    login_as_user,
    register_user,
)


def test_api_challenges_get_visibility_public():
    """Can a public user get /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_ctftime_public():
    """Can a public user get /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            set_config(
                "start", "1507089600"
            )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config(
                "end", "1507262400"
            )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get("/api/v1/challenges")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_visibility_private():
    """Can a private user get /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_get_ctftime_private():
    """Can a private user get /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get("/api/v1/challenges")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_verified_emails():
    """Can a verified email user get /api/v1/challenges"""
    app = create_ctfd()
    with app.app_context():
        set_config("verify_emails", True)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges", json="")
        assert r.status_code == 403
        gen_user(
            app.db,
            name="user_name",
            email="verified_user@examplectf.com",
            password="password",
            verified=True,
        )
        registered_client = login_as_user(app, "user_name", "password")
        r = registered_client.get("/api/v1/challenges")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_post_non_admin():
    """Can a user post /api/v1/challenges if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.post("/api/v1/challenges", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_admin():
    """Can a user GET /api/v1/challenges if admin without team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_challenge(app.db)
        # Admin does not have a team but should still be able to see challenges
        user = Users.query.filter_by(id=1).first()
        assert user.team_id is None
        with login_as_user(app, "admin") as admin:
            r = admin.get("/api/v1/challenges", json="")
            assert r.status_code == 200
            r = admin.get("/api/v1/challenges/1", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_get_hidden_admin():
    """Can an admin see hidden challenges in API list response"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, state="hidden")
        gen_challenge(app.db)

        with login_as_user(app, "admin") as admin:
            challenges_list = admin.get("/api/v1/challenges", json="").get_json()[
                "data"
            ]
            assert len(challenges_list) == 1
            challenges_list = admin.get(
                "/api/v1/challenges?view=admin", json=""
            ).get_json()["data"]
            assert len(challenges_list) == 2
    destroy_ctfd(app)


def test_api_challenges_get_solve_status():
    """Does the challenge list API show the current user's solve status?"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db).id
        register_user(app)
        client = login_as_user(app)
        # First request - unsolved
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solved_by_me"] is False
        # Solve and re-request
        gen_solve(app.db, user_id=2, challenge_id=chal_id)
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solved_by_me"] is True
    destroy_ctfd(app)


def test_api_challenges_get_solve_count():
    """Does the challenge list API show the solve count?"""
    # This is checked with public requests against the API after each generated
    # user makes a solve
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id
        with app.test_client() as client:
            _USER_BASE = 2  # First user we create will have this ID
            _MAX = 3  # arbitrarily selected
            for i in range(_MAX):
                # Confirm solve count against `i` first
                r = client.get("/api/v1/challenges")
                assert r.status_code == 200
                chal_data = r.get_json()["data"].pop()
                assert chal_data["solves"] == i
                # Generate a new user and solve for the challenge
                uname = "user{}".format(i)
                uemail = uname + "@examplectf.com"
                register_user(app, name=uname, email=uemail)
                gen_solve(app.db, user_id=_USER_BASE + i, challenge_id=chal_id)
            # Confirm solve count one final time against `_MAX`
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            chal_data = r.get_json()["data"].pop()
            assert chal_data["solves"] == _MAX
    destroy_ctfd(app)


def test_api_challenges_get_solve_info_score_visibility():
    """Does the challenge list API show solve info if scores are hidden?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as pub_client:
        set_config("challenge_visibility", "public")

        # Generate a challenge, user and solve to test the API with
        chal_id = gen_challenge(app.db).id
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        #  With the public setting any unauthed user should see the solve
        set_config("score_visibility", "public")
        r = pub_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] == False

        # With the private setting only an authed user should see the solve
        set_config("score_visibility", "private")
        # Test public user
        r = pub_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is False
        # Test authed user
        user_client = login_as_user(app)
        r = user_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is True

        # With the admins setting only admins should see the solve
        set_config("score_visibility", "admins")
        # Test authed user
        r = user_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is True
        # Test admin
        admin_client = login_as_user(app, "admin", "password")
        r = admin_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the hidden setting nobody should see the solve
        set_config("score_visibility", "hidden")
        r = admin_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] is None
    destroy_ctfd(app)


def test_api_challenges_get_solve_info_account_visibility():
    """Does the challenge list API show solve info if accounts are hidden?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as pub_client:
        set_config("challenge_visibility", "public")

        # Generate a challenge, user and solve to test the API with
        chal_id = gen_challenge(app.db).id
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        #  With the public setting any unauthed user should see the solve
        set_config("account_visibility", "public")
        r = pub_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the private setting only an authed user should see the solve
        set_config("account_visibility", "private")
        # Test public user
        r = pub_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is False
        # Test user
        user_client = login_as_user(app)
        r = user_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is True

        # With the admins setting only admins should see the solve
        set_config("account_visibility", "admins")
        # Test user
        r = user_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is True
        # Test admin user
        admin_client = login_as_user(app, "admin", "password")
        r = admin_client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False
    destroy_ctfd(app)


def test_api_challenges_get_solve_count_frozen():
    """Does the challenge list API count solves made during a freeze?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as client:
        set_config("challenge_visibility", "public")
        set_config("freeze", "1507262400")
        chal_id = gen_challenge(app.db).id

        with freeze_time("2017-10-4"):
            # Create a user and generate a solve from before the freeze time
            register_user(app, name="user1", email="user1@examplectf.com")
            gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Confirm solve count is now `1`
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1

        with freeze_time("2017-10-8"):
            # Create a user and generate a solve from after the freeze time
            register_user(app, name="user2", email="user2@examplectf.com")
            gen_solve(app.db, user_id=3, challenge_id=chal_id)

        # Confirm solve count is still `1` despite the new solve
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        chal_data = r.get_json()["data"].pop()
        assert chal_data["solves"] == 1
    destroy_ctfd(app)


def test_api_challenges_get_solve_count_hidden_user():
    """Does the challenge list API show solve counts for hidden users?"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id
        # The admin is expected to be hidden by default
        gen_solve(app.db, user_id=1, challenge_id=chal_id)
        with app.test_client() as client:
            # Confirm solve count is `0` despite the hidden admin having solved
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            chal_data = r.get_json()["data"].pop()
            assert chal_data["solves"] == 0
        # We expect the admin to be able to see their own solve
        with login_as_user(app, "admin") as admin:
            r = admin.get("/api/v1/challenges")
            assert r.status_code == 200
            chal_data = r.get_json()["data"].pop()
            assert chal_data["solves"] == 0
            assert chal_data["solved_by_me"] is True
    destroy_ctfd(app)


def test_api_challenges_get_solve_count_banned_user():
    """Does the challenge list API show solve counts for banned users?"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id

        # Create a banned user and generate a solve for the challenge
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Confirm that the solve is there
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            chal_data = r.get_json()["data"].pop()
            assert chal_data["solves"] == 1

        # Ban the user
        with login_as_user(app, name="admin") as client:
            r = client.patch("/api/v1/users/2", json={"banned": True})
        assert Users.query.get(2).banned == True

        with app.test_client() as client:
            # Confirm solve count is `0` despite the banned user having solved
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            chal_data = r.get_json()["data"].pop()
            assert chal_data["solves"] == 0
    destroy_ctfd(app)


def test_api_challenges_get_type_with_visibility():
    """Can users see challenges which override visibility in API list response?
    """
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        # Confirm the challenge is shown with no mocking done
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200
        assert len(r.json["data"]) == 1
        # Confirm that `is_visible()` is called and the challenge is only shown
        # if it returns truthy.
        for rv in {True, False, "thisalsoworks", 0}:
            with mock.patch(
                "CTFd.plugins.challenges.BaseChallenge.is_visible", return_value=rv
            ) as mock_is_visible:
                r = client.get("/api/v1/challenges")
            assert mock_is_visible.call_count == 1
            assert r.status_code == 200
            assert len(r.json["data"]) == (1 if rv else 0)
    destroy_ctfd(app)


def test_api_challenges_get_type_with_visibility_admin():
    """Can admin see challenges which override visibility in API list response?
    """
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app, "admin")
        # Confirm that if admin makes a normal request, the usual behaviour is
        # followed and the challenge is only shown if `is_visible()` is truthy
        for rv in {True, False}:
            with mock.patch(
                "CTFd.plugins.challenges.BaseChallenge.is_visible", return_value=rv
            ) as mock_is_visible:
                r = client.get("/api/v1/challenges")
            assert mock_is_visible.call_count == 1
            assert r.status_code == 200
            assert len(r.json["data"]) == (1 if rv else 0)
        # Confirm that if admin requests the admin view, `is_visible()` is not
        # called and the challenge is shown regardless of its return value
        for rv in {True, False}:
            with mock.patch(
                "CTFd.plugins.challenges.BaseChallenge.is_visible", return_value=rv
            ) as mock_is_visible:
                r = client.get("/api/v1/challenges?view=admin")
            assert mock_is_visible.call_count == 0
            assert r.status_code == 200
            assert len(r.json["data"]) == 1
    destroy_ctfd(app)


def test_api_challenges_post_admin():
    """Can a user post /api/v1/challenges if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.post(
                "/api/v1/challenges",
                json={
                    "name": "chal",
                    "category": "cate",
                    "description": "desc",
                    "value": "100",
                    "state": "hidden",
                    "type": "standard",
                },
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_types_post_non_admin():
    """Can a non-admin get /api/v1/challenges/types if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/types", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_types_post_admin():
    """Can an admin get /api/v1/challenges/types if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/challenges/types", json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_visibility_public():
    """Can a public user get /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        with app.test_client() as client:
            gen_challenge(app.db)
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_ctftime_public():
    """Can a public user get /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config("challenge_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 200
            set_config(
                "start", "1507089600"
            )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config(
                "end", "1507262400"
            )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get("/api/v1/challenges/1")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_visibility_private():
    """Can a private user get /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_with_admin_only_account_visibility():
    """Can a private user get /api/v1/challenges/<challenge_id> if account_visibility is admins_only"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        set_config("account_visibility", "admins")
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_ctftime_private():
    """Can a private user get /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_verified_emails():
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
            email="verified_user@examplectf.com",
            password="password",
            verified=True,
        )
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, "user_name", "password")
        r = client.get("/api/v1/challenges/1", json="")
        assert r.status_code == 403
        r = registered_client.get("/api/v1/challenges/1")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_non_existing():
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


def test_api_challenge_get_solve_status():
    """Does the challenge detail API show the current user's solve status?"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)
        register_user(app)
        client = login_as_user(app)
        # First request - unsolved
        r = client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solved_by_me"] is False
        # Solve and re-request
        gen_solve(app.db, user_id=2, challenge_id=chal_id)
        r = client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solved_by_me"] is True
    destroy_ctfd(app)


def test_api_challenge_get_solve_info_score_visibility():
    """Does the challenge detail API show solve info if scores are hidden?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as pub_client:
        set_config("challenge_visibility", "public")
        # Generate a challenge, user and solve to test the API with
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        #  With the public setting any unauthed user should see the solve
        set_config("score_visibility", "public")
        r = pub_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the private setting only an authed user should see the solve
        set_config("score_visibility", "private")
        # Test public user
        r = pub_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is False
        # Test user
        user_client = login_as_user(app)
        r = user_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is True

        # With the admins setting only admins should see the solve
        set_config("score_visibility", "admins")
        # Test user
        r = user_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is True
        # Test admin user
        admin_client = login_as_user(app, "admin", "password")
        r = admin_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the hidden setting nobody should see the solve
        set_config("score_visibility", "hidden")
        r = admin_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] is None
    destroy_ctfd(app)


def test_api_challenge_get_solve_info_account_visibility():
    """Does the challenge detail API show solve info if accounts are hidden?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as pub_client:
        set_config("challenge_visibility", "public")
        # Generate a challenge, user and solve to test the API with
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        #  With the public setting any unauthed user should see the solve
        set_config("account_visibility", "public")
        r = pub_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the private setting only an authed user should see the solve
        set_config("account_visibility", "private")
        # Test public user
        r = pub_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is False
        # Test user
        user_client = login_as_user(app)
        r = user_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is True

        # With the admins setting only admins should see the solve
        set_config("account_visibility", "admins")
        # Test user
        r = user_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] is None
        assert chal_data["solved_by_me"] is True
        # Test admin user
        admin_client = login_as_user(app, "admin", "password")
        r = admin_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
        assert chal_data["solved_by_me"] is False

        # With the hidden setting admins can still see the solve
        # because the challenge detail endpoint doesn't have an admin specific view
        set_config("account_visibility", "hidden")
        r = admin_client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
    destroy_ctfd(app)


def test_api_challenge_get_solve_count():
    """Does the challenge detail API show the solve count?"""
    # This is checked with public requests against the API after each generated
    # user makes a solve
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)
        with app.test_client() as client:
            _USER_BASE = 2  # First user we create will have this ID
            _MAX = 3  # arbitrarily selected
            for i in range(_MAX):
                # Confirm solve count against `i` first
                r = client.get(chal_uri)
                assert r.status_code == 200
                chal_data = r.get_json()["data"]
                assert chal_data["solves"] == i
                # Generate a new user and solve for the challenge
                uname = "user{}".format(i)
                uemail = uname + "@examplectf.com"
                register_user(app, name=uname, email=uemail)
                gen_solve(app.db, user_id=_USER_BASE + i, challenge_id=chal_id)
            # Confirm solve count one final time against `_MAX`
            r = client.get(chal_uri)
            assert r.status_code == 200
            chal_data = r.get_json()["data"]
            assert chal_data["solves"] == _MAX
    destroy_ctfd(app)


def test_api_challenge_get_solve_count_frozen():
    """Does the challenge detail API count solves made during a freeze?"""
    app = create_ctfd()
    with app.app_context(), app.test_client() as client:
        set_config("challenge_visibility", "public")
        # Friday, October 6, 2017 4:00:00 AM
        set_config("freeze", "1507262400")
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)

        with freeze_time("2017-10-4"):
            # Create a user and generate a solve from before the freeze time
            register_user(app, name="user1", email="user1@examplectf.com")
            gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Confirm solve count is now `1`
        r = client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1

        with freeze_time("2017-10-8"):
            # Create a user and generate a solve from after the freeze time
            register_user(app, name="user2", email="user2@examplectf.com")
            gen_solve(app.db, user_id=3, challenge_id=chal_id)

        # Confirm solve count is still `1` despite the new solve
        r = client.get(chal_uri)
        assert r.status_code == 200
        chal_data = r.get_json()["data"]
        assert chal_data["solves"] == 1
    destroy_ctfd(app)


def test_api_challenge_get_solve_count_hidden_user():
    """Does the challenge detail API show solve counts for hidden users?"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)
        # The admin is expected to be hidden by default
        gen_solve(app.db, user_id=1, challenge_id=chal_id)
        with app.test_client() as client:
            # Confirm solve count is `0` despite the hidden admin having solved
            r = client.get(chal_uri)
            assert r.status_code == 200
            chal_data = r.get_json()["data"]
            assert chal_data["solves"] == 0
    destroy_ctfd(app)


def test_api_challenge_get_solve_count_banned_user():
    """Does the challenge detail API show solve counts for banned users?"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        chal_id = gen_challenge(app.db).id
        chal_uri = "/api/v1/challenges/{}".format(chal_id)

        # Create a user and generate a solve for the challenge
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Confirm that the solve is there
        with app.test_client() as client:
            r = client.get(chal_uri)
            assert r.status_code == 200
            chal_data = r.get_json()["data"]
            assert chal_data["solves"] == 1

        # Ban the user
        with login_as_user(app, name="admin") as client:
            r = client.patch("/api/v1/users/2", json={"banned": True})
        assert Users.query.get(2).banned == True

        # Confirm solve count is `0` despite the banned user having solved
        with app.test_client() as client:
            r = client.get(chal_uri)
            assert r.status_code == 200
            chal_data = r.get_json()["data"]
            assert chal_data["solves"] == 0
    destroy_ctfd(app)


def test_api_challenge_get_type_with_visibility():
    """Can users see challenges which override visibility in API detail response?
    """
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        # Confirm the challenge is shown with no mocking done
        r = client.get("/api/v1/challenges/1")
        assert r.status_code == 200
        # Confirm that `is_visible()` is called and the challenge is only shown
        # if it returns truthy.
        for rv in {True, False, "thisalsoworks", 0}:
            with mock.patch(
                "CTFd.plugins.challenges.BaseChallenge.is_visible", return_value=rv
            ) as mock_is_visible:
                r = client.get("/api/v1/challenges/1")
            assert mock_is_visible.call_count == 1
            assert r.status_code == (200 if rv else 404)
    destroy_ctfd(app)


def test_api_challenge_get_type_with_visibility_admin():
    """Can admin see challenges which override visibility in API detail response?
    """
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app, "admin")
        # Confirm that if admin makes a normal request, `is_visible()` is not
        # called and the challenge is shown regardless of its return value
        for rv in {True, False}:
            with mock.patch(
                "CTFd.plugins.challenges.BaseChallenge.is_visible", return_value=rv
            ) as mock_is_visible:
                r = client.get("/api/v1/challenges/1")
            assert mock_is_visible.call_count == 0
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_patch_non_admin():
    """Can a user patch /api/v1/challenges/<challenge_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.patch("/api/v1/challenges/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_patch_admin():
    """Can a user patch /api/v1/challenges/<challenge_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/challenges/1", json={"name": "chal_name", "value": "200"}
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["value"] == 200
    destroy_ctfd(app)


def test_api_challenge_delete_non_admin():
    """Can a user delete /api/v1/challenges/<challenge_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.delete("/api/v1/challenges/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_delete_admin():
    """Can a user delete /api/v1/challenges/<challenge_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/challenges/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
    destroy_ctfd(app)


def test_api_challenge_with_properties_delete_admin():
    """Can a user delete /api/v1/challenges/<challenge_id> if the challenge has other properties"""
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_hint(app.db, challenge_id=challenge.id)
        gen_tag(app.db, challenge_id=challenge.id)
        gen_flag(app.db, challenge_id=challenge.id)

        challenge = Challenges.query.filter_by(id=1).first()
        assert len(challenge.hints) == 1
        assert len(challenge.tags) == 1
        assert len(challenge.flags) == 1

        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/challenges/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None

        assert Tags.query.count() == 0
        assert Hints.query.count() == 0
        assert Flags.query.count() == 0

    destroy_ctfd(app)


def test_api_challenge_attempt_post_public():
    """Can a public user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.post("/api/v1/challenges/attempt", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_attempt_post_private():
    """Can an private user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        challenge_id = gen_challenge(app.db).id
        gen_flag(app.db, challenge_id)
        register_user(app)
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "wrong_flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "incorrect"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "already_solved"
        challenge_id = gen_challenge(app.db).id
        gen_flag(app.db, challenge_id)
        with login_as_user(app) as client:
            for _ in range(10):
                gen_fail(app.db, user_id=2, challenge_id=challenge_id)
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 429
            assert r.get_json()["data"]["status"] == "ratelimited"
    destroy_ctfd(app)

    app = create_ctfd(user_mode="teams")
    with app.app_context():
        challenge_id = gen_challenge(app.db).id
        gen_flag(app.db, challenge_id)
        register_user(app)
        team_id = gen_team(app.db).id
        user = Users.query.filter_by(id=2).first()
        user.team_id = team_id
        app.db.session.commit()
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "wrong_flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "incorrect"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "already_solved"
        challenge_id = gen_challenge(app.db).id
        gen_flag(app.db, challenge_id)
        with login_as_user(app) as client:
            for _ in range(10):
                gen_fail(app.db, user_id=2, team_id=team_id, challenge_id=challenge_id)
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": challenge_id, "submission": "flag"},
            )
            assert r.status_code == 429
            assert r.get_json()["data"]["status"] == "ratelimited"
    destroy_ctfd(app)


def test_api_challenge_attempt_post_admin():
    """Can an admin user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        with login_as_user(app, "admin") as client:
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": 1, "submission": "wrong_flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "incorrect"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": 1, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "correct"
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": 1, "submission": "flag"},
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["status"] == "already_solved"
    destroy_ctfd(app)


def test_api_challenge_get_solves_visibility_public():
    """Can a public user get /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            set_config("challenge_visibility", "public")
            r = client.get("/api/v1/challenges/1/solves", json="")
            assert r.status_code == 200
            set_config("challenge_visibility", "private")
            r = client.get("/api/v1/challenges/1/solves", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_ctftime_public():
    """Can a public user get /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config("challenge_visibility", "public")
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/solves")
            assert r.status_code == 200
            set_config(
                "start", "1507089600"
            )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config(
                "end", "1507262400"
            )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get("/api/v1/challenges/1/solves", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_ctf_frozen():
    """Test users can only see challenge solves that happened before freeze time"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_solve(app.db, user_id=2, challenge_id=chal_id)
            chal2 = gen_challenge(app.db)
            chal2_id = chal2.id

        with freeze_time("2017-10-8"):
            # User ID 2 solves Challenge ID 2
            gen_solve(app.db, user_id=2, challenge_id=chal2_id)
            # User ID 3 solves Challenge ID 1
            gen_solve(app.db, user_id=3, challenge_id=chal_id)

            # Challenge 1 has 2 solves
            # Challenge 2 has 1 solve

            # There should now be two solves assigned to the same user.
            assert Solves.query.count() == 3

            client = login_as_user(app, name="user2")

            # Challenge 1 should have one solve (after freeze)
            r = client.get("/api/v1/challenges/1")
            data = r.get_json()["data"]
            assert data["solves"] == 1

            # Challenge 1 should have one solve (after freeze)
            r = client.get("/api/v1/challenges/1/solves")
            data = r.get_json()["data"]
            assert len(data) == 1

            # Challenge 2 should have a solve shouldn't be shown to the user
            r = client.get("/api/v1/challenges/2/solves")
            data = r.get_json()["data"]
            assert len(data) == 0

            # Admins should see data as an admin with no modifications
            admin = login_as_user(app, name="admin")
            r = admin.get("/api/v1/challenges/2/solves")
            data = r.get_json()["data"]
            assert len(data) == 1

            # But should see as a user if the preview param is passed
            r = admin.get("/api/v1/challenges/2/solves?preview=true")
            data = r.get_json()["data"]
            assert len(data) == 0

    destroy_ctfd(app)


def test_api_challenge_get_solves_visibility_private():
    """Can a private user get /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
        set_config("challenge_visibility", "public")
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_solves_ctftime_private():
    """Can a private user get /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_verified_emails():
    """Can a verified email get /api/v1/challenges/<challenge_id>/solves"""
    app = create_ctfd()
    with app.app_context():
        set_config("verify_emails", True)
        gen_challenge(app.db)
        gen_user(
            app.db,
            name="user_name",
            email="verified_user@examplectf.com",
            password="password",
            verified=True,
        )
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, "user_name", "password")
        r = client.get("/api/v1/challenges/1/solves", json="")
        assert r.status_code == 403
        r = registered_client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_get_solves_score_visibility():
    """Can a user get /api/v1/challenges/<challenge_id>/solves if score_visibility is public/private/admin"""
    app = create_ctfd()
    with app.app_context():
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


def test_api_challenge_get_solves_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id>/solves 404"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/api/v1/challenges/1/solves")
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_solves_returns_correct_data():
    """Test that /api/v1/<challenge_id>/solves returns expected data"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, challenge_id=chal.id)
        r = client.get("/api/v1/challenges/1/solves")
        resp = r.get_json()["data"]
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get("account_id") == 2
        assert solve.get("name") == "user"
        assert solve.get("date") is not None
        assert solve.get("account_url") == "/users/2"
    destroy_ctfd(app)

    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        app.db.session.commit()
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, team_id=1, challenge_id=chal.id)
        r = client.get("/api/v1/challenges/1/solves")
        resp = r.get_json()["data"]
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get("account_id") == 1
        assert solve.get("name") == "team_name"
        assert solve.get("date") is not None
        assert solve.get("account_url") == "/teams/1"
    destroy_ctfd(app)

    app = create_ctfd(application_root="/ctf")
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, challenge_id=chal.id)
        r = client.get("/api/v1/challenges/1/solves")
        resp = r.get_json()["data"]
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get("account_id") == 2
        assert solve.get("name") == "user"
        assert solve.get("date") is not None
        assert solve.get("account_url") == "/ctf/users/2"
    destroy_ctfd(app)


def test_api_challenge_get_files_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/files if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/files", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_files_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/files if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/challenges/1/files")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_tags_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/tags if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/tags", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_tags_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/tags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/challenges/1/tags")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_topics_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/topics if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/topics", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_topics_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/topics if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_topic(app.db, challenge_id=1)
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/challenges/1/topics", json="")
            assert r.status_code == 200
            assert r.get_json() == {
                "success": True,
                "data": [{"id": 1, "challenge_id": 1, "topic_id": 1, "value": "topic"}],
            }
    destroy_ctfd(app)


def test_api_challenge_get_hints_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/hints if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/hints", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_hints_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/hints if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/challenges/1/hints")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_flags_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/flags if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges/1/flags", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_flags_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/flags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/challenges/1/flags")
            assert r.status_code == 200
    destroy_ctfd(app)
