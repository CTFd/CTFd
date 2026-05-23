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


def test_api_challenges_challenge_with_requirements_anonymize_preview():
    """Does the challenge list API show preview anonymized challenge details?"""
    app = create_ctfd()
    with app.app_context():
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id], "anonymize": "preview"}
        chal_id = chal_obj.id
        chal_name = chal_obj.name
        chal_category = chal_obj.category
        chal_value = chal_obj.value
        register_user(app)

        with login_as_user(app) as client:
            # ChallengeList for preview anonymize shows identifying details but type "hidden"
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 2
            locked = next(c for c in data if c["id"] == chal_id)
            assert locked["type"] == "hidden"
            assert locked["name"] == chal_name
            assert locked["value"] == chal_value
            assert locked["category"] == chal_category
            assert locked["solved_by_me"] is False

            # Challenge for preview anonymize shows details but type "hidden"
            r = client.get(f"/api/v1/challenges/{chal_id}")
            assert r.status_code == 200
            locked_data = r.get_json()["data"]
            assert locked_data["type"] == "hidden"
            assert locked_data["name"] == chal_name
            assert locked_data["value"] == chal_value
            assert locked_data["category"] == chal_category

        # After solving the prerequisite, the challenge is fully visible
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{chal_id}")
            assert r.status_code == 200
            assert r.get_json()["data"]["type"] == "standard"
    destroy_ctfd(app)


def test_api_challenges_challenge_with_requirements_anonymize_true():
    """Does the challenge list API show fully anonymized challenges when requirements aren't met?"""
    app = create_ctfd()
    with app.app_context():
        prereq_id = gen_challenge(app.db).id
        chal_obj = gen_challenge(app.db)
        chal_obj.requirements = {"prerequisites": [prereq_id], "anonymize": True}
        chal_id = chal_obj.id
        chal_name = chal_obj.name
        register_user(app)

        with login_as_user(app) as client:
            # List endpoint: full anonymize shows "???" placeholders
            r = client.get("/api/v1/challenges")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert len(data) == 2
            locked = next(c for c in data if c["id"] == chal_id)
            assert locked["type"] == "hidden"
            assert locked["name"] == "???"
            assert locked["value"] == 0
            assert locked["category"] == "???"
            assert locked["tags"] == []
            assert locked["solved_by_me"] is False

            # Single challenge endpoint: returns anonymized "???"
            r = client.get(f"/api/v1/challenges/{chal_id}")
            assert r.status_code == 200
            locked_data = r.get_json()["data"]
            assert locked_data["type"] == "hidden"
            assert locked_data["name"] == "???"
            assert locked_data["value"] == 0
            assert locked_data["category"] == "???"

        # After solving the prerequisite, the challenge is fully visible
        gen_solve(app.db, user_id=2, challenge_id=prereq_id)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{chal_id}")
            assert r.status_code == 200
            assert r.get_json()["data"]["name"] == chal_name
    destroy_ctfd(app)


def test_api_challenges_locked_detail_includes_prerequisites():
    """Locked challenge detail responses include prerequisite names so users know what to solve."""
    app = create_ctfd()
    with app.app_context():
        prereq = gen_challenge(app.db)
        prereq_id = prereq.id
        prereq_name = prereq.name

        preview_chal = gen_challenge(app.db, name="preview-locked")
        preview_chal.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": "preview",
        }
        preview_chal_id = preview_chal.id

        anon_chal = gen_challenge(app.db, name="fully-locked")
        anon_chal.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": True,
        }
        anon_chal_id = anon_chal.id
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{preview_chal_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["type"] == "hidden"
            assert data["requirements"]["prerequisites"] == {
                "named": [{"id": prereq_id, "name": prereq_name}],
                "anonymous_count": 0,
            }

            r = client.get(f"/api/v1/challenges/{anon_chal_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["type"] == "hidden"
            assert data["name"] == "???"
            assert data["requirements"]["prerequisites"] == {
                "named": [{"id": prereq_id, "name": prereq_name}],
                "anonymous_count": 0,
            }
    destroy_ctfd(app)


def test_api_challenges_unlocks_field_anonymize_modes():
    """Unlocked detail responses expose dependents via `unlocks`, respecting anonymize."""
    app = create_ctfd()
    with app.app_context():
        prereq = gen_challenge(app.db, name="prereq")
        prereq_id = prereq.id

        preview_dep = gen_challenge(app.db, name="preview-dep")
        preview_dep.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": "preview",
        }
        preview_dep_id = preview_dep.id
        anon_dep = gen_challenge(app.db, name="anon-dep")
        anon_dep.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": True,
        }
        hidden_dep = gen_challenge(app.db, name="hidden-dep")
        hidden_dep.requirements = {"prerequisites": [prereq_id]}
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{prereq_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert "unlocks" in data
            assert data["unlocks"]["named"] == [
                {"id": preview_dep_id, "name": "preview-dep"}
            ]
            assert data["unlocks"]["anonymous_count"] == 2
    destroy_ctfd(app)


def test_api_challenges_unlocks_excludes_already_solved_dependents():
    """If a user has already solved a dependent challenge, it should not appear in `unlocks`."""
    app = create_ctfd()
    with app.app_context():
        prereq = gen_challenge(app.db, name="prereq")
        prereq_id = prereq.id

        dep = gen_challenge(app.db, name="dep")
        dep.requirements = {"prerequisites": [prereq_id], "anonymize": "preview"}
        dep_id = dep.id
        app.db.session.commit()

        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=dep_id)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{prereq_id}")
            assert r.status_code == 200
            assert r.get_json()["data"]["unlocks"] == {
                "named": [],
                "anonymous_count": 0,
            }
    destroy_ctfd(app)


def test_api_challenges_unlocks_admin_view_shows_all_names():
    """Admins viewing a challenge see all dependent names regardless of anonymize."""
    app = create_ctfd()
    with app.app_context():
        prereq = gen_challenge(app.db, name="prereq")
        prereq_id = prereq.id

        anon_dep = gen_challenge(app.db, name="anon-dep")
        anon_dep.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": True,
        }
        anon_dep_id = anon_dep.id
        app.db.session.commit()

        with login_as_user(app, name="admin") as admin:
            r = admin.get(f"/api/v1/challenges/{prereq_id}")
            assert r.status_code == 200
            unlocks = r.get_json()["data"]["unlocks"]
            assert unlocks == {
                "named": [{"id": anon_dep_id, "name": "anon-dep"}],
                "anonymous_count": 0,
            }
    destroy_ctfd(app)


def test_api_challenges_locked_prerequisites_respect_anonymize_of_prereqs():
    """When listing prereqs of a locked challenge, prereqs that themselves are hidden do not leak their names."""
    app = create_ctfd()
    with app.app_context():
        invisible_gate = gen_challenge(app.db, name="invisible-gate", state="hidden")
        invisible_gate_id = invisible_gate.id

        anon_prereq = gen_challenge(app.db, name="test-anonymize")
        anon_prereq.requirements = {
            "prerequisites": [invisible_gate_id],
            "anonymize": True,
        }
        anon_prereq_id = anon_prereq.id

        false_prereq = gen_challenge(app.db, name="test-hidden")
        false_prereq.requirements = {
            "prerequisites": [invisible_gate_id],
            "anonymize": False,
        }
        false_prereq_id = false_prereq.id

        nested = gen_challenge(app.db, name="test-nested")
        nested.requirements = {
            "prerequisites": [anon_prereq_id, false_prereq_id],
            "anonymize": "preview",
        }
        nested_id = nested.id
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{nested_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            prereq_payload = data["requirements"]["prerequisites"]
            assert prereq_payload["named"] == []
            assert prereq_payload["anonymous_count"] == 2
            view = data["view"]
            assert "test-anonymize" not in view
            assert "test-hidden" not in view
    destroy_ctfd(app)


def test_api_challenges_locked_anonymize_true_view_does_not_leak_name_or_value():
    """For anonymize=True locked challenges, the rendered `view` HTML do not contain the challenge name or value."""
    app = create_ctfd()
    with app.app_context():
        prereq = gen_challenge(app.db, name="prereq")
        prereq_id = prereq.id

        secret_name = "super-secret-challenge"
        secret_value = 4242
        anon_chal = gen_challenge(app.db, name=secret_name, value=secret_value)
        anon_chal.requirements = {
            "prerequisites": [prereq_id],
            "anonymize": True,
        }
        anon_chal_id = anon_chal.id
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{anon_chal_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["name"] == "???"
            assert data["value"] == 0
            view = data.get("view", "")
            assert secret_name not in view
            assert str(secret_value) not in view
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
