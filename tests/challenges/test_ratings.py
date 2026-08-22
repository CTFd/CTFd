#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.cache import clear_ratings
from CTFd.models import Ratings
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_rating,
    gen_solve,
    login_as_user,
    register_user,
)


def test_ratings_public_config():
    """Test that users can see and leave ratings when configuration is set to public"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Create users and challenge
        register_user(app, name="user1", email="user1@example.com")
        user1_id = 2
        register_user(app, name="user2", email="user2@example.com")
        user2_id = 3
        register_user(app, name="user3", email="user3@example.com")
        user3_id = 4
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        challenge_id = challenge.id
        gen_flag(app.db, challenge_id=challenge_id, content="flag{test}")

        # Solve the challenge for both users (required to rate)
        gen_solve(
            app.db, user_id=user1_id, challenge_id=challenge_id, provided="flag{test}"
        )
        gen_solve(
            app.db, user_id=user2_id, challenge_id=challenge_id, provided="flag{test}"
        )
        gen_solve(
            app.db, user_id=user3_id, challenge_id=challenge_id, provided="flag{test}"
        )

        client1 = login_as_user(app, name="user1", password="password")
        client2 = login_as_user(app, name="user2", password="password")
        client3 = login_as_user(app, name="user3", password="password")

        # Test that users can leave ratings (PUT request)
        rating_data1 = {
            "value": 1,
            "review": "Great challenge! Really enjoyed solving it.",
        }
        r = client1.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data1)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Great challenge! Really enjoyed solving it."
        assert data["data"]["challenge_id"] == challenge_id

        # Second user can also rate
        rating_data2 = {"value": 1, "review": "Excellent challenge!"}
        r = client2.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data2)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Excellent challenge!"

        # Second user can also rate
        rating_data3 = {"value": -1, "review": "Hated it!"}
        r = client3.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data3)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == -1
        assert data["data"]["review"] == "Hated it!"

        # Test that challenge detail includes rating info when public
        r = client1.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert "ratings" in data["data"]
        assert data["data"]["ratings"]["up"] == 2
        assert data["data"]["ratings"]["down"] == 1
        assert data["data"]["ratings"]["count"] == 3
        assert "rating" in data["data"]  # User's own rating
        assert data["data"]["rating"]["value"] == 1
        assert (
            data["data"]["rating"]["review"]
            == "Great challenge! Really enjoyed solving it."
        )
        assert len(Ratings.query.all()) == 3

    destroy_ctfd(app)


def test_ratings_private_config():
    """Test that users can only leave ratings but cannot see aggregated ratings when set to private"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "private")

        # Create users and challenge
        register_user(app, name="user1", email="user1@example.com")
        user1_id = 2
        register_user(app, name="user2", email="user2@example.com")
        user2_id = 3
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        challenge_id = challenge.id
        gen_flag(app.db, challenge_id=challenge_id, content="flag{test}")

        # Solve the challenge for both users (required to rate)
        gen_solve(
            app.db, user_id=user1_id, challenge_id=challenge_id, provided="flag{test}"
        )
        gen_solve(
            app.db, user_id=user2_id, challenge_id=challenge_id, provided="flag{test}"
        )

        client1 = login_as_user(app, name="user1", password="password")
        client2 = login_as_user(app, name="user2", password="password")
        admin_client = login_as_user(app, name="admin", password="password")

        # Test that non-admin users cannot see aggregated ratings (GET request should fail)
        r = client1.get(f"/api/v1/challenges/{challenge_id}/ratings", json=True)
        assert r.status_code == 403  # Forbidden

        # Test that users can still leave ratings (PUT request)
        rating_data1 = {"value": 1, "review": "Good challenge with private rating"}
        r = client1.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data1)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Good challenge with private rating"

        # Second user can also rate
        rating_data2 = {"value": 1, "review": "Excellent private challenge!"}
        r = client2.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data2)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Excellent private challenge!"

        # Test that challenge detail doesn't include aggregated ratings for regular users
        r = client1.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["ratings"] is None  # No aggregated ratings shown
        assert "rating" in data["data"]  # But user can see their own rating
        assert data["data"]["rating"]["value"] == 1
        assert data["data"]["rating"]["review"] == "Good challenge with private rating"

        # Test that admin can still see aggregated ratings
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["meta"]["summary"]["up"] == 2
        assert data["meta"]["summary"]["down"] == 0
        assert data["meta"]["summary"]["count"] == 2

        assert len(Ratings.query.all()) == 2

    destroy_ctfd(app)


def test_ratings_disabled_config():
    """Test that users cannot see or leave ratings when ratings are disabled"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "disabled")

        # Create users and challenge
        register_user(app, name="user1", email="user1@example.com")
        user1_id = 2
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        challenge_id = challenge.id
        gen_flag(app.db, challenge_id=challenge_id, content="flag{test}")

        # Solve the challenge (required to rate)
        gen_solve(
            app.db, user_id=user1_id, challenge_id=challenge_id, provided="flag{test}"
        )

        client1 = login_as_user(app, name="user1", password="password")
        admin_client = login_as_user(app, name="admin", password="password")

        # Test that users cannot see ratings (GET request should fail)
        r = client1.get(f"/api/v1/challenges/{challenge_id}/ratings", json=True)
        assert r.status_code == 403  # Forbidden

        # Test that users cannot leave ratings (PUT request should fail)
        rating_data = {"value": 2, "review": "Trying to rate when disabled"}
        r = client1.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data)
        assert r.status_code == 403  # Forbidden
        assert len(Ratings.query.all()) == 0

        # Test that challenge detail doesn't include any rating info
        r = client1.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["ratings"] is None
        assert data["data"]["rating"] is None

        # Test that even admin cannot leave ratings when disabled
        r = admin_client.put(
            f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data
        )
        assert r.status_code == 403  # Forbidden

        # But admin can still see the endpoint (though it will be empty)
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings", json=True)
        data = r.get_json()
        assert len(data["data"]) == 0

        assert len(Ratings.query.all()) == 0

    destroy_ctfd(app)


def test_rating_requires_solve():
    """Test that users can only rate challenges they have solved"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Create a user and challenge
        register_user(app, name="user1", email="user1@example.com")
        user_id = 2
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        chal_id = challenge.id
        gen_flag(app.db, challenge_id=chal_id, content="flag{test}")

        client = login_as_user(app, name="user1", password="password")

        # Try to rate without solving first
        rating_data = {"value": 1, "review": "Great challenge!"}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 403
        data = r.get_json()
        assert data["success"] is False
        assert "You must solve this challenge before rating it" in data["errors"][""][0]
        assert len(Ratings.query.all()) == 0

        # Now solve the challenge
        gen_solve(app.db, user_id=user_id, challenge_id=chal_id, provided="flag{test}")

        # Now rating should work
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Great challenge!"
        assert len(Ratings.query.all()) == 1

    destroy_ctfd(app)


def test_rating_validation():
    """Test rating input validation"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Create a user and challenge
        register_user(app, name="user1", email="user1@example.com")
        user_id = 2
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        chal_id = challenge.id
        gen_flag(app.db, challenge_id=chal_id, content="flag{test}")

        # Solve the challenge
        gen_solve(app.db, user_id=user_id, challenge_id=chal_id, provided="flag{test}")

        client = login_as_user(app, name="user1", password="password")

        # Test missing rating value
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json={})
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value is required" in data["errors"]["value"][0]

        # Test invalid rating value (not -1 or 1)
        rating_data = {"value": 0}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be either 1 or -1" in data["errors"]["value"][0]

        # Test invalid rating value (too high)
        rating_data = {"value": 2}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be either 1 or -1" in data["errors"]["value"][0]

        # Test invalid rating value (non-integer)
        rating_data = {"value": "invalid"}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be an integer" in data["errors"]["value"][0]

        # Test review text too long
        long_review = "x" * 2001  # Exceeds 2000 character limit
        rating_data = {"value": 1, "review": long_review}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert (
            "Review text cannot exceed 2000 characters" in data["errors"]["review"][0]
        )
        assert len(Ratings.query.all()) == 0

        # Test valid rating with review
        rating_data = {
            "value": -1,
            "review": "This is a valid review within the character limit.",
        }
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == -1
        assert (
            data["data"]["review"]
            == "This is a valid review within the character limit."
        )
        assert len(Ratings.query.all()) == 1

    destroy_ctfd(app)


def test_rating_update():
    """Test that users can update their existing ratings"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Create a user and challenge
        register_user(app, name="user1", email="user1@example.com")
        user_id = 2
        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        chal_id = challenge.id
        gen_flag(app.db, challenge_id=challenge.id, content="flag{test}")

        # Solve the challenge
        gen_solve(app.db, user_id=user_id, challenge_id=chal_id, provided="flag{test}")

        client = login_as_user(app, name="user1", password="password")

        # Create initial rating
        initial_rating = {"value": 1, "review": "Initial review"}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=initial_rating)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 1
        assert data["data"]["review"] == "Initial review"
        initial_id = data["data"]["id"]
        assert len(Ratings.query.all()) == 1
        r = Ratings.query.get(1)
        assert r.value == 1
        assert r.review == "Initial review"

        # Update the rating
        updated_rating = {
            "value": -1,
            "review": "Updated review after thinking more about it",
        }
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=updated_rating)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == -1
        assert data["data"]["review"] == "Updated review after thinking more about it"
        assert data["data"]["id"] == initial_id  # Same rating record, just updated
        assert len(Ratings.query.all()) == 1

        r = Ratings.query.get(1)
        assert r.value == -1
        assert r.review == "Updated review after thinking more about it"

        # Verify only one rating exists in database
        ratings = Ratings.query.filter_by(user_id=user_id, challenge_id=chal_id).all()
        assert len(ratings) == 1
        assert ratings[0].value == -1
        assert ratings[0].review == "Updated review after thinking more about it"

    destroy_ctfd(app)


def test_rating_without_authentication():
    """Test that unauthenticated users cannot rate challenges"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        gen_flag(app.db, challenge_id=challenge.id, content="flag{test}")

        # Try to rate without being logged in
        with app.test_client() as client:
            rating_data = {"value": 4, "review": "Great challenge!"}
            r = client.put(
                f"/api/v1/challenges/{challenge.id}/ratings", json=rating_data
            )
            assert r.status_code == 403
            assert len(Ratings.query.all()) == 0

    destroy_ctfd(app)


def test_ratings_upvote_downvote_count():
    """Test that upvote and downvote calculations are correct with multiple users and ratings"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Define test data for upvote/downvote ratings
        user_ratings = [
            {
                "name": "user1",
                "email": "user1@example.com",
                "value": 1,  # upvote
                "review": "Excellent challenge!",
            },
            {
                "name": "user2",
                "email": "user2@example.com",
                "value": -1,  # downvote
                "review": "Not great",
            },
            {
                "name": "user3",
                "email": "user3@example.com",
                "value": 1,  # upvote
                "review": "Pretty good!",
            },
        ]

        # Expected upvotes/downvotes after each rating submission
        expected_counts = [
            {"up": 1, "down": 0, "count": 1},  # After user1
            {"up": 1, "down": 1, "count": 2},  # After user2
            {"up": 2, "down": 1, "count": 3},  # After user3
        ]

        # Create users and challenge
        users = []
        user_ids = []
        user_id_start = 2
        for rating_data in user_ratings:
            user = register_user(
                app, name=rating_data["name"], email=rating_data["email"]
            )
            users.append(user)
            user_ids.append(user_id_start)  # Store ID immediately
            user_id_start += 1

        # Create admin client for accessing ratings endpoint
        admin_client = login_as_user(app, name="admin", password="password")

        challenge = gen_challenge(app.db, name="Test Challenge", value=100)
        challenge_id = challenge.id  # Store ID immediately
        gen_flag(app.db, challenge_id=challenge_id, content="flag{test}")

        # Solve the challenge for all users (required to rate)
        for user_id in user_ids:
            gen_solve(
                app.db,
                user_id=user_id,
                challenge_id=challenge_id,
                provided="flag{test}",
            )

        # Initially no ratings - check admin can see empty ratings endpoint
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["meta"]["summary"]["up"] == 0
        assert data["meta"]["summary"]["down"] == 0
        assert data["meta"]["summary"]["count"] == 0

        # Submit ratings progressively and verify calculations using database creation
        for i, rating_data in enumerate(user_ratings):
            # Create rating directly in database using helper
            gen_rating(
                app.db,
                user_id=user_ids[i],
                challenge_id=challenge_id,
                value=rating_data["value"],
                review=rating_data["review"],
            )

            assert len(Ratings.query.all()) == i + 1

            # Check admin ratings endpoint has correct upvote/downvote counts
            r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["meta"]["summary"]["up"] == expected_counts[i]["up"]
            assert data["meta"]["summary"]["down"] == expected_counts[i]["down"]
            assert data["meta"]["summary"]["count"] == expected_counts[i]["count"]

        # Verify each user can see their own correct rating in challenge detail
        for rating_data in user_ratings:
            user_client = login_as_user(
                app, name=rating_data["name"], password="password"
            )
            r = user_client.get(f"/api/v1/challenges/{challenge_id}")
            data = r.get_json()
            assert data["data"]["rating"]["value"] == rating_data["value"]
            assert data["data"]["rating"]["review"] == rating_data["review"]

        # Test rating update - user 1 changes their rating from upvote (1) to downvote (-1)
        # Update rating directly in database
        first_rating = Ratings.query.filter_by(
            user_id=user_ids[0], challenge_id=challenge_id
        ).first()
        first_rating.value = -1  # Change from upvote to downvote
        first_rating.review = "Actually, not so great after reconsidering"
        app.db.session.commit()
        clear_ratings()

        assert len(Ratings.query.all()) == len(
            user_ratings
        )  # Still same number of ratings

        # Update the expected values list for verification
        user_ratings[0]["value"] = -1
        user_ratings[0]["review"] = "Actually, not so great after reconsidering"

        # Expected counts after update: user1 changed from upvote to downvote
        # So now we have: user1(-1), user2(-1), user3(1) = 1 upvote, 2 downvotes
        expected_updated_counts = {"up": 1, "down": 2, "count": 3}

        # Check counts after update using admin ratings endpoint
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
        assert r.status_code == 200
        data = r.get_json()
        print(data)
        assert data["success"] is True
        assert data["meta"]["summary"]["up"] == expected_updated_counts["up"]
        assert data["meta"]["summary"]["down"] == expected_updated_counts["down"]
        assert data["meta"]["summary"]["count"] == expected_updated_counts["count"]

        # Verify updated user sees their new rating in challenge detail
        user1_client = login_as_user(app, name="user1", password="password")
        r = user1_client.get(f"/api/v1/challenges/{challenge_id}")
        data = r.get_json()
        assert data["data"]["rating"]["value"] == -1
        assert (
            data["data"]["rating"]["review"]
            == "Actually, not so great after reconsidering"
        )

        # Verify all other users still see their original ratings in challenge detail
        for user in user_ratings:
            user_client = login_as_user(
                app, name=user["name"], password="password", raise_for_error=False
            )
            r = user_client.get(f"/api/v1/challenges/{challenge_id}")
            data = r.get_json()
            assert data["data"]["rating"]["value"] == user["value"]
            assert data["data"]["rating"]["review"] == user["review"]

        # Verify database consistency
        all_ratings = Ratings.query.filter_by(challenge_id=challenge_id).all()
        assert len(all_ratings) == len(user_ratings)
        rating_values = [r.value for r in all_ratings]
        expected_values = sorted([rating["value"] for rating in user_ratings])
        assert sorted(rating_values) == expected_values

        # Verify counts match database reality
        upvotes = sum(1 for value in rating_values if value == 1)
        downvotes = sum(1 for value in rating_values if value == -1)
        assert upvotes == expected_updated_counts["up"]
        assert downvotes == expected_updated_counts["down"]

    destroy_ctfd(app)
