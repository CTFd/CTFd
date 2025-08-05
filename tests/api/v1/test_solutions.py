#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Challenges, Solutions, SolutionUnlocks
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    ctftime,
    destroy_ctfd,
    gen_challenge,
    gen_solution,
    gen_user,
    login_as_user,
    register_user,
)


def test_api_solutions_get_list_non_admin():
    """Can a non-admin user get /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/solutions", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_get_list_public():
    """Can a public user get /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/solutions", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_get_list_admin():
    """Can an admin user get /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id

        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/solutions", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["id"] == solution_id
    destroy_ctfd(app)


def test_api_solutions_post_non_admin():
    """Can a non-admin user post /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)

        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/solutions",
                json={"challenge_id": 1, "content": "test solution", "state": "hidden"},
            )
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_post_public():
    """Can a public user post /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)

        with app.test_client() as client:
            r = client.post(
                "/api/v1/solutions",
                json={"challenge_id": 1, "content": "test solution", "state": "hidden"},
            )
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_post_admin():
    """Can an admin user post /api/v1/solutions"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)

        with login_as_user(app, "admin") as client:
            r = client.post(
                "/api/v1/solutions",
                json={"challenge_id": 1, "content": "test solution", "state": "hidden"},
            )
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["challenge_id"] == 1
            assert data["data"]["content"] == "test solution"
            assert data["data"]["state"] == "hidden"

            # Verify solution was created in database
            solution = Solutions.query.filter_by(challenge_id=1).first()
            assert solution is not None
            assert solution.content == "test solution"
    destroy_ctfd(app)


def test_api_solutions_post_admin_default_state():
    """Does posting a solution without state default to 'hidden'"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)

        with login_as_user(app, "admin") as client:
            r = client.post(
                "/api/v1/solutions",
                json={"challenge_id": 1, "content": "test solution"},
            )
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["state"] == "hidden"
    destroy_ctfd(app)


def test_api_solutions_get_detail_public():
    """Can a public user get /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution = gen_solution(app.db, challenge_id=1)

        with app.test_client() as client:
            r = client.get(f"/api/v1/solutions/{solution.id}", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_get_detail_non_admin_locked():
    """Can a non-admin user get /api/v1/solutions/<solution_id> when locked"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id
        register_user(app)

        with login_as_user(app) as client:
            r = client.get(f"/api/v1/solutions/{solution_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should only show locked fields
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" not in data["data"]
            assert "html" not in data["data"]
    destroy_ctfd(app)


def test_api_solutions_get_detail_non_admin_unlocked():
    """Can a non-admin user get /api/v1/solutions/<solution_id> when unlocked"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id
        user_id = gen_user(app.db, name="user", email="user@user.com").id

        # Create solution unlock
        unlock = SolutionUnlocks(user_id=user_id, target=solution_id)
        app.db.session.add(unlock)
        app.db.session.commit()

        with login_as_user(app, name="user", password="password") as client:
            r = client.get(f"/api/v1/solutions/{solution_id}", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should show unlocked fields
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" in data["data"]
            assert "html" in data["data"]
    destroy_ctfd(app)


def test_api_solutions_get_detail_admin():
    """Can an admin user get /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id

        with login_as_user(app, "admin") as client:
            r = client.get(f"/api/v1/solutions/{solution_id}", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should show all admin fields
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" in data["data"]
            assert "html" in data["data"]
    destroy_ctfd(app)


def test_api_solutions_patch_non_admin():
    """Can a non-admin user patch /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id
        register_user(app)

        with login_as_user(app) as client:
            r = client.patch(
                f"/api/v1/solutions/{solution_id}", json={"content": "updated solution"}
            )
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_patch_public():
    """Can a public user patch /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution = gen_solution(app.db, challenge_id=1)

        with app.test_client() as client:
            r = client.patch(
                f"/api/v1/solutions/{solution.id}", json={"content": "updated solution"}
            )
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_patch_admin():
    """Can an admin user patch /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(
            app.db, challenge_id=1, content="original content"
        ).id

        with login_as_user(app, "admin") as client:
            r = client.patch(
                f"/api/v1/solutions/{solution_id}", json={"content": "updated solution"}
            )
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["content"] == "updated solution"

            # Verify solution was updated in database
            updated_solution = Solutions.query.get(solution_id)
            assert updated_solution.content == "updated solution"
    destroy_ctfd(app)


def test_api_solutions_delete_non_admin():
    """Can a non-admin user delete /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution_id = gen_solution(app.db, challenge_id=1).id
        register_user(app)

        with login_as_user(app) as client:
            r = client.delete(f"/api/v1/solutions/{solution_id}", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_delete_public():
    """Can a public user delete /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution = gen_solution(app.db, challenge_id=1)

        with app.test_client() as client:
            r = client.delete(f"/api/v1/solutions/{solution.id}", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_solutions_delete_admin():
    """Can an admin user delete /api/v1/solutions/<solution_id>"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        solution = gen_solution(app.db, challenge_id=1)
        solution_id = solution.id

        with login_as_user(app, "admin") as client:
            r = client.delete(f"/api/v1/solutions/{solution.id}", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True

            # Verify solution was deleted from database
            deleted_solution = Solutions.query.get(solution_id)
            assert deleted_solution is None
    destroy_ctfd(app)


def test_api_solutions_get_list_with_query_params():
    """Can an admin user get /api/v1/solutions with query parameters"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_challenge(app.db)

        # Create solutions with different states
        solution1_id = gen_solution(app.db, challenge_id=1, state="hidden").id
        solution2_id = gen_solution(app.db, challenge_id=2, state="visible").id

        with login_as_user(app, "admin") as client:
            # Test filtering by state
            r = client.get("/api/v1/solutions?state=hidden", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["id"] == solution1_id

            # Test filtering by different state
            r = client.get("/api/v1/solutions?state=visible", json="")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["id"] == solution2_id
    destroy_ctfd(app)


def test_api_solutions_get_detail_not_found():
    """Does getting a non-existent solution return 404"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.get("/api/v1/solutions/999", json="")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_solutions_patch_not_found():
    """Does patching a non-existent solution return 404"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/solutions/999", json={"content": "updated solution"}
            )
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_solutions_delete_not_found():
    """Does deleting a non-existent solution return 404"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/solutions/999", json="")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_includes_solution_id_when_visible():
    """Does the challenge detail API include solution_id when a visible solution exists"""
    app = create_ctfd()
    with app.app_context():
        # Create a challenge
        challenge = gen_challenge(app.db)
        challenge_id = challenge.id

        # Test 1: Challenge without solution should have solution_id = None
        with login_as_user(app, "admin") as client:
            r = client.get(f"/api/v1/challenges/{challenge_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["solution_id"] is None

        # Test 2: Challenge with hidden solution should have solution_id = None
        solution = gen_solution(app.db, challenge_id=challenge_id, state="hidden")
        solution_id = solution.id

        with login_as_user(app, "admin") as client:
            r = client.get(f"/api/v1/challenges/{challenge_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["solution_id"] is None

        # Test 3: Challenge with visible solution should include solution_id
        solution = Solutions.query.filter_by(id=1).first()
        solution.state = "visible"
        app.db.session.commit()

        with login_as_user(app, "admin") as client:
            r = client.get(f"/api/v1/challenges/{challenge_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            print(data)
            assert data["data"]["solution_id"] == solution_id

        # Test 4: Non-admin users should also see solution_id for visible solutions
        register_user(app)
        with login_as_user(app) as client:
            r = client.get(f"/api/v1/challenges/{challenge_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["solution_id"] == solution_id

    destroy_ctfd(app)


def test_api_user_cannot_view_solution_until_unlocked():
    """Test that a regular user cannot view a solution until it is unlocked via the API"""
    app = create_ctfd()
    with app.app_context():
        # Create a challenge and solution
        challenge = gen_challenge(app.db)
        challenge_id = challenge.id
        solution = gen_solution(
            app.db,
            challenge_id=challenge_id,
            content="This is the solution",
            state="visible",
        )
        solution_id = solution.id

        # Create a regular user
        user = gen_user(app.db, name="testuser", email="test@example.com")
        user_id = user.id

        # User cannot see solution content when locked
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.get(f"/api/v1/solutions/{solution_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should only show locked fields
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" not in data["data"]
            assert "html" not in data["data"]

        # Unlock the solution via API
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.post(
                "/api/v1/unlocks", json={"target": solution_id, "type": "solutions"}
            )
            assert r.status_code == 200
            unlock_data = r.get_json()
            assert unlock_data["success"] is True
            assert unlock_data["data"]["target"] == solution_id
            assert unlock_data["data"]["type"] == "solutions"
            assert unlock_data["data"]["user_id"] == user_id

        unlock = SolutionUnlocks.query.filter_by(
            user_id=user_id, target=solution_id
        ).first()
        assert unlock is not None
        assert unlock.user_id == user_id
        assert unlock.target == solution_id

        # User can now see solution content when unlocked
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.get(f"/api/v1/solutions/{solution_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should show unlocked fields
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" in data["data"]
            assert "html" in data["data"]
            assert data["data"]["content"] == "This is the solution"

        # Attempting to unlock again should fail
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.post(
                "/api/v1/unlocks", json={"target": solution_id, "type": "solutions"}
            )
            assert r.status_code == 400
            error_data = r.get_json()
            assert error_data["success"] is False
            assert (
                "You've already unlocked this target" in error_data["errors"]["target"]
            )

    destroy_ctfd(app)


def test_api_solutions_cannot_be_viewed_before_ctf_starts():
    """Test that solutions cannot be viewed before the CTF starts"""
    app = create_ctfd()
    with app.app_context():
        # Set up CTF timing
        with ctftime.init():
            # Create a challenge and solution
            challenge = gen_challenge(app.db)
            solution = gen_solution(
                app.db,
                challenge_id=challenge.id,
                content="Hidden solution",
                state="visible",
            )
            solution_id = solution.id

            # Create a regular user
            gen_user(app.db, name="testuser", email="test@example.com")

            # Test before CTF starts - should return 403
            with ctftime.not_started():
                with login_as_user(app, name="testuser", password="password") as client:
                    r = client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 403

                # Admin can always see solutions
                with login_as_user(app, "admin") as admin_client:
                    r = admin_client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 200
                    data = r.get_json()

            # Test during CTF - should work normally
            with ctftime.started():  # During CTF
                with login_as_user(app, name="testuser", password="password") as client:
                    r = client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 200
                    data = r.get_json()
                    assert data["success"] is True
                    # Should show locked fields for non-admin user
                    assert "id" in data["data"]
                    assert "challenge_id" in data["data"]
                    assert "state" in data["data"]
                    assert (
                        "content" not in data["data"]
                    )  # Still locked for regular user

                # Admin should see full content during CTF
                with login_as_user(app, "admin") as admin_client:
                    r = admin_client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 200
                    data = r.get_json()
                    assert data["success"] is True
                    assert "content" in data["data"]
                    assert data["data"]["content"] == "Hidden solution"

            # Test after CTF ends - should return 403
            with ctftime.ended():
                # Admins can always see solutions, even after CTF ends
                with login_as_user(app, "admin") as admin_client:
                    r = admin_client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 200

                with login_as_user(app, name="testuser", password="password") as client:
                    r = client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 403
                    data = r.get_json()

                    set_config("view_after_ctf", True)
                    r = client.get(f"/api/v1/solutions/{solution_id}")
                    assert r.status_code == 200
                    data = r.get_json()
                    assert data["success"] is True

    destroy_ctfd(app)


def test_api_solutions_cannot_be_viewed_if_challenge_is_hidden():
    """Test that solutions cannot be viewed if the associated challenge is hidden"""
    app = create_ctfd()
    with app.app_context():
        # Create a hidden challenge and solution
        hidden_challenge = gen_challenge(app.db, state="hidden")
        hidden_solution = gen_solution(
            app.db,
            challenge_id=hidden_challenge.id,
            content="Hidden challenge solution",
            state="visible",
        )
        hidden_solution_id = hidden_solution.id

        # Create a regular user
        user = gen_user(app.db, name="testuser", email="test@example.com")
        user_id = user.id

        # Regular user cannot access solution for hidden challenge
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.get(f"/api/v1/solutions/{hidden_solution_id}")
            assert r.status_code == 403

        # Admin can access solution for hidden challenge
        with login_as_user(app, "admin") as admin_client:
            r = admin_client.get(f"/api/v1/solutions/{hidden_solution_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert "content" in data["data"]
            assert data["data"]["content"] == "Hidden challenge solution"

        # Even if user unlocks the solution, they still can't see it if challenge is hidden
        # First, unlock the solution for the hidden challenge
        unlock = SolutionUnlocks(user_id=user_id, target=hidden_solution_id)
        app.db.session.add(unlock)
        app.db.session.commit()

        # User still cannot access the solution because the challenge is hidden
        with login_as_user(app, name="testuser", password="password") as client:
            r = client.get(f"/api/v1/solutions/{hidden_solution_id}")
            assert r.status_code == 403

        # Make the challenge visible, now user should be able to see the unlocked solution
        challenge = Challenges.query.filter_by(id=1).first()
        challenge.state = "visible"
        app.db.session.commit()

        with login_as_user(app, name="testuser", password="password") as client:
            r = client.get(f"/api/v1/solutions/{hidden_solution_id}")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            # Should show unlocked fields since user has unlocked it and challenge is now visible
            assert "id" in data["data"]
            assert "challenge_id" in data["data"]
            assert "state" in data["data"]
            assert "content" in data["data"]
            assert "html" in data["data"]
            assert data["data"]["content"] == "Hidden challenge solution"

    destroy_ctfd(app)
