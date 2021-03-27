#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_solve,
    login_as_user,
    register_user,
)


def test_api_challenges_admins_can_bypass_requirements():
    """Test that admins can bypass requirements checks with admin capabilities and view-admin"""
    app = create_ctfd()
    with app.app_context():
        # Create challenges
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id]}

        register_user(app)
        # Confirm that regular users cannot see prerequisites
        with login_as_user(app) as client:
            # Locked challenges aren't shown
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 1
            assert data[0]["id"] == 1

            # Not even with tricks
            r = client.get("/api/v1/challenges?view=admin")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 1
            assert data[0]["id"] == 1

            # Not even with forced browsing
            r = client.get("/api/v1/challenges/2")
            assert r.status_code == 403

        # Confirm that admins
        with login_as_user(app, name="admin") as admin:
            # Admins see as regular users
            r = admin.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 1
            assert data[0]["id"] == 1

            # Now admins can see all challenges
            r = admin.get("/api/v1/challenges?view=admin")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 2
            assert data[0]["id"] == 1
            assert data[1]["id"] == 2

            # Admins can force browse to challenges
            r = admin.get("/api/v1/challenges/2")
            assert r.status_code == 200
            assert r.get_json()["data"]
    destroy_ctfd(app)


def test_api_challenges_challenge_with_requirements():
    """Does the challenge list API show challenges with requirements met?"""
    app = create_ctfd()
    with app.app_context():
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id]}
        chal_id = chal_obj.id
        # Create a new user which will solve the prerequisite
        register_user(app)
        # Confirm that only the prerequisite challenge is listed initially
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            (chal_data,) = r.get_json()["data"]
            assert chal_data["id"] == prereq_id
        # Generate a solve and then confirm the second challenge is visible
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 2
            chal_ids = {c["id"] for c in r.get_json()["data"]}
            assert chal_ids == {prereq_id, chal_id}
    destroy_ctfd(app)


def test_api_challenges_challenge_with_requirements_hidden_user():
    """Does the challenge list API show gated challenges to a hidden user?"""
    app = create_ctfd()
    with app.app_context():
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id]}
        chal_id = chal_obj.id
        # Create a new user which will solve the prerequisite and hide them
        register_user(app)
        Users.query.get(2).hidden = True
        app.db.session.commit()
        # Confirm that only the prerequisite challenge is listed initially
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            (chal_data,) = r.get_json()["data"]
            assert chal_data["id"] == prereq_id
        # Generate a solve and then confirm the second challenge is visible
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 2
            chal_ids = {c["id"] for c in r.get_json()["data"]}
            assert chal_ids == {prereq_id, chal_id}
    destroy_ctfd(app)


def test_api_challenges_challenge_with_requirements_banned_user():
    """Does the challenge list API show gated challenges to a banned user?"""
    app = create_ctfd()
    with app.app_context():
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id]}
        # Create a new user which will solve the prerequisite and ban them
        register_user(app)
        Users.query.get(2).banned = True
        app.db.session.commit()
        # Generate a solve just in case and confirm the API 403s
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with login_as_user(app) as client:
            assert client.get("/api/v1/challenges").status_code == 403
    destroy_ctfd(app)


def test_api_challenges_challenge_with_requirements_no_user():
    """Does the challenge list API show gated challenges to the public?"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "public")
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id]}
        # Create a new user which will solve the prerequisite
        register_user(app)
        # Confirm that only the prerequisite challenge is listed publicly
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            initial_data = r.get_json()["data"]
            (chal_data,) = initial_data
            assert chal_data["id"] == prereq_id
            # Fix up the solve count for later comparison with `initial_data`
            chal_data["solves"] += 1
        # Generate a solve and then confirm the response is unchanged
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with app.test_client() as client:
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            assert r.get_json()["data"] == initial_data
    destroy_ctfd(app)
