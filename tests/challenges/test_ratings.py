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

        # Test that users can leave ratings (PUT request)
        rating_data1 = {
            "value": 4,
            "review": "Great challenge! Really enjoyed solving it.",
        }
        r = client1.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data1)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 4
        assert data["data"]["review"] == "Great challenge! Really enjoyed solving it."
        assert data["data"]["challenge_id"] == challenge_id

        # Second user can also rate
        rating_data2 = {"value": 5, "review": "Excellent challenge!"}
        r = client2.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data2)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 5
        assert data["data"]["review"] == "Excellent challenge!"

        # Test that challenge detail includes rating info when public
        r = client1.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert "ratings" in data["data"]
        assert data["data"]["ratings"]["average"] == 4.5
        assert data["data"]["ratings"]["count"] == 2
        assert "rating" in data["data"]  # User's own rating
        assert data["data"]["rating"]["value"] == 4
        assert (
            data["data"]["rating"]["review"]
            == "Great challenge! Really enjoyed solving it."
        )
        assert len(Ratings.query.all()) == 2

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
        rating_data1 = {"value": 3, "review": "Good challenge with private rating"}
        r = client1.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data1)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 3
        assert data["data"]["review"] == "Good challenge with private rating"

        # Second user can also rate
        rating_data2 = {"value": 5, "review": "Excellent private challenge!"}
        r = client2.put(f"/api/v1/challenges/{challenge_id}/ratings", json=rating_data2)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 5
        assert data["data"]["review"] == "Excellent private challenge!"

        # Test that challenge detail doesn't include aggregated ratings for regular users
        r = client1.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["ratings"] is None  # No aggregated ratings shown
        assert "rating" in data["data"]  # But user can see their own rating
        assert data["data"]["rating"]["value"] == 3
        assert data["data"]["rating"]["review"] == "Good challenge with private rating"

        # Test that admin can still see aggregated ratings
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["meta"]["summary"]["average"] == 4.0  # (3+5)/2
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
        rating_data = {"value": 4, "review": "Great challenge!"}
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
        assert data["data"]["value"] == 4
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

        # Test invalid rating value (too low)
        rating_data = {"value": 0}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be between 1 and 5" in data["errors"]["value"][0]

        # Test invalid rating value (too high)
        rating_data = {"value": 6}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be between 1 and 5" in data["errors"]["value"][0]

        # Test invalid rating value (non-integer)
        rating_data = {"value": "invalid"}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 400
        data = r.get_json()
        assert data["success"] is False
        assert "Rating value must be an integer" in data["errors"]["value"][0]

        # Test review text too long
        long_review = "x" * 2001  # Exceeds 2000 character limit
        rating_data = {"value": 4, "review": long_review}
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
            "value": 4,
            "review": "This is a valid review within the character limit.",
        }
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=rating_data)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 4
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
        initial_rating = {"value": 3, "review": "Initial review"}
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=initial_rating)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 3
        assert data["data"]["review"] == "Initial review"
        initial_id = data["data"]["id"]
        assert len(Ratings.query.all()) == 1
        r = Ratings.query.get(1)
        assert r.value == 3
        assert r.review == "Initial review"

        # Update the rating
        updated_rating = {
            "value": 5,
            "review": "Updated review after thinking more about it",
        }
        r = client.put(f"/api/v1/challenges/{chal_id}/ratings", json=updated_rating)
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["data"]["value"] == 5
        assert data["data"]["review"] == "Updated review after thinking more about it"
        assert data["data"]["id"] == initial_id  # Same rating record, just updated
        assert len(Ratings.query.all()) == 1

        r = Ratings.query.get(1)
        assert r.value == 5
        assert r.review == "Updated review after thinking more about it"

        # Verify only one rating exists in database
        ratings = Ratings.query.filter_by(user_id=user_id, challenge_id=chal_id).all()
        assert len(ratings) == 1
        assert ratings[0].value == 5
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


def test_ratings_average_and_count():
    """Test that average and count calculations are correct with multiple users and ratings"""
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_ratings", "public")

        # Define test data for ratings
        user_ratings = [
            {
                "name": "user1",
                "email": "user1@example.com",
                "value": 5,
                "review": "Excellent challenge!",
            },
            {
                "name": "user2",
                "email": "user2@example.com",
                "value": 3,
                "review": "It was okay",
            },
            {
                "name": "user3",
                "email": "user3@example.com",
                "value": 1,
                "review": "Too difficult",
            },
        ]

        # Expected averages after each rating submission
        expected_averages = [5.0, 4.0, 3.0]

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
        assert data["meta"]["summary"]["average"] is None
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

            # Check admin ratings endpoint has correct average and count
            r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["meta"]["summary"]["average"] == expected_averages[i]
            assert data["meta"]["summary"]["count"] == i + 1

        # Verify each user can see their own correct rating in challenge detail
        for rating_data in user_ratings:
            user_client = login_as_user(
                app, name=rating_data["name"], password="password"
            )
            r = user_client.get(f"/api/v1/challenges/{challenge_id}")
            data = r.get_json()
            assert data["data"]["rating"]["value"] == rating_data["value"]
            assert data["data"]["rating"]["review"] == rating_data["review"]

        # Test rating update - user 1 changes their rating from 5 to 4
        # Update rating directly in database
        first_rating = Ratings.query.filter_by(
            user_id=user_ids[0], challenge_id=challenge_id
        ).first()
        first_rating.value = 4
        first_rating.review = "Good challenge, revised rating"
        app.db.session.commit()
        clear_ratings()

        assert len(Ratings.query.all()) == len(
            user_ratings
        )  # Still same number of ratings

        # Update the expected values list for verification
        user_ratings[0]["value"] = 4
        user_ratings[0]["review"] = "Good challenge, revised rating"
        updated_values = [rating["value"] for rating in user_ratings]
        expected_updated_average = round(
            sum(updated_values) / len(updated_values), 1
        )  # Should be 2.6 (4+3+1)/3

        # Check average after update using admin ratings endpoint
        r = admin_client.get(f"/api/v1/challenges/{challenge_id}/ratings")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert data["meta"]["summary"]["average"] == expected_updated_average
        assert data["meta"]["summary"]["count"] == len(user_ratings)

        # Verify updated user sees their new rating in challenge detail
        user1_client = login_as_user(app, name="user1", password="password")
        r = user1_client.get(f"/api/v1/challenges/{challenge_id}")
        data = r.get_json()
        assert data["data"]["rating"]["value"] == 4
        assert data["data"]["rating"]["review"] == "Good challenge, revised rating"

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
        assert (
            round(sum(rating_values) / len(rating_values), 1)
            == expected_updated_average
        )

    destroy_ctfd(app)
