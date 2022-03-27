#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time

from CTFd.models import Awards, Fails, Solves, Users
from CTFd.schemas.users import UserSchema
from CTFd.utils import set_config
from CTFd.utils.crypto import verify_password
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_fail,
    gen_solve,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_api_users_get_public():
    """Can a user get /api/v1/users if users are public"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/users")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_users_get_private():
    """Can a user get /api/v1/users if users are public"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/users")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_users_get_admins():
    """Can a user get /api/v1/users if users are public"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/users")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_users_post_non_admin():
    """Can a user post /api/v1/users if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.post("/api/v1/users", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_users_post_admin():
    """Can a user post /api/v1/users if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            # Create user
            r = client.post(
                "/api/v1/users",
                json={"name": "user", "email": "user@user.com", "password": "password"},
            )
            assert r.status_code == 200

            # Make sure password was hashed properly
            user = Users.query.filter_by(email="user@user.com").first()
            assert user
            assert verify_password("password", user.password)

            # Make sure user can login with the creds
            client = login_as_user(app)
            r = client.get("/profile")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_users_post_admin_with_attributes():
    """Can a user post /api/v1/users with user settings"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            # Create user
            r = client.post(
                "/api/v1/users",
                json={
                    "name": "user",
                    "email": "user@user.com",
                    "password": "password",
                    "banned": True,
                    "hidden": True,
                    "verified": True,
                },
            )
            assert r.status_code == 200

            # Make sure password was hashed properly
            user = Users.query.filter_by(email="user@user.com").first()
            assert user
            assert verify_password("password", user.password)
            assert user.banned
            assert user.hidden
            assert user.verified
    destroy_ctfd(app)


def test_api_users_post_admin_duplicate_information():
    """Can an admin create a user with duplicate information"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, "admin") as client:
            # Duplicate email
            r = client.post(
                "/api/v1/users",
                json={
                    "name": "user2",
                    "email": "user@examplectf.com",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["email"]
            assert resp["success"] is False
            assert Users.query.count() == 2

            # Duplicate user
            r = client.post(
                "/api/v1/users",
                json={
                    "name": "user",
                    "email": "user2@examplectf.com",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["name"]
            assert resp["success"] is False
            assert Users.query.count() == 2
    destroy_ctfd(app)


def test_api_users_patch_admin_duplicate_information():
    """Can an admin modify a user with duplicate information"""
    app = create_ctfd()
    with app.app_context():
        register_user(
            app, name="user1", email="user1@examplectf.com", password="password"
        )
        register_user(
            app, name="user2", email="user2@examplectf.com", password="password"
        )
        with login_as_user(app, "admin") as client:
            # Duplicate name
            r = client.patch(
                "/api/v1/users/1",
                json={
                    "name": "user2",
                    "email": "user@examplectf.com",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["name"]
            assert resp["success"] is False

            # Duplicate email
            r = client.patch(
                "/api/v1/users/1",
                json={
                    "name": "user",
                    "email": "user2@examplectf.com",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["email"]
            assert resp["success"] is False
            assert Users.query.count() == 3
    destroy_ctfd(app)


def test_api_users_patch_duplicate_information():
    """Can a user modify their information to another user's"""
    app = create_ctfd()
    with app.app_context():
        register_user(
            app, name="user1", email="user1@examplectf.com", password="password"
        )
        register_user(
            app, name="user2", email="user2@examplectf.com", password="password"
        )
        with login_as_user(app, "user1") as client:
            # Duplicate email
            r = client.patch(
                "/api/v1/users/me",
                json={
                    "name": "user1",
                    "email": "user2@examplectf.com",
                    "confirm": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["email"]
            assert resp["success"] is False

            # Duplicate user
            r = client.patch(
                "/api/v1/users/me",
                json={
                    "name": "user2",
                    "email": "user1@examplectf.com",
                    "confirm": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["name"]
            assert resp["success"] is False
            assert Users.query.count() == 3
    destroy_ctfd(app)


def test_api_team_get_public():
    """Can a user get /api/v1/team/<user_id> if users are public"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            gen_user(app.db)
            r = client.get("/api/v1/users/2")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_private():
    """Can a user get /api/v1/users/<user_id> if users are private"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/users/2")
            print(r.__dict__)
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_admin():
    """Can a user get /api/v1/users/<user_id> if users are viewed by admins only"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, "admin") as client:
            gen_user(app.db)
            set_config("account_visibility", "public")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/users/2")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_patch_non_admin():
    """Can a user patch /api/v1/users/<user_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with app.test_client() as client:
            r = client.patch("/api/v1/users/2", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_patch_admin():
    """Can a user patch /api/v1/users/<user_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/users/2",
                json={
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "country": "US",
                    "verified": True,
                },
            )
            assert r.status_code == 200
            user_data = r.get_json()["data"]
            assert user_data["country"] == "US"
            assert user_data["verified"] is True
    destroy_ctfd(app)


def test_api_user_delete_non_admin():
    """Can a user delete /api/v1/users/<user_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with app.test_client() as client:
            r = client.delete("/api/v1/teams/2", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_delete_admin():
    """Can a user patch /api/v1/users/<user_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user=user)
        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/users/2", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None
        assert Users.query.filter_by(id=2).first() is None
    destroy_ctfd(app)


def test_api_user_get_me_not_logged_in():
    """Can a user get /api/v1/users/me if not logged in"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/users/me")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_user_get_me_logged_in():
    """Can a user get /api/v1/users/me if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/me")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_patch_me_not_logged_in():
    """Can a user patch /api/v1/users/me if not logged in"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.patch("/api/v1/users/me", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_patch_me_logged_in():
    """Can a user patch /api/v1/users/me if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.patch(
                "/api/v1/users/me",
                json={
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "confirm": "password",
                    "country": "US",
                },
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["country"] == "US"
    destroy_ctfd(app)


def test_api_admin_user_patch_me_logged_in():
    """Can an admin patch /api/v1/users/me"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, name="admin") as client:
            r = client.patch(
                "/api/v1/users/me",
                json={
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "confirm": "password",
                    "country": "US",
                },
            )
            assert r.status_code == 200
            assert r.get_json()["data"]["country"] == "US"

            user = Users.query.filter_by(id=1).first()
            assert user.name == "user"
            assert user.email == "user@examplectf.com"
    destroy_ctfd(app)


def test_api_user_change_name():
    """Can a user change their name via the API"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.patch("/api/v1/users/me", json={"name": "user2"})
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["name"] == "user2"
            assert resp["success"] is True

            r = client.patch("/api/v1/users/me", json={"name": None})
            resp = r.get_json()
            print(resp)
            assert r.status_code == 400
            assert resp["errors"]["name"] == ["Field may not be null."]
            assert resp["success"] is False

            set_config("name_changes", False)

            r = client.patch("/api/v1/users/me", json={"name": "new_name"})
            assert r.status_code == 400
            resp = r.get_json()
            assert "name" in resp["errors"]
            assert resp["success"] is False

            set_config("name_changes", True)
            r = client.patch("/api/v1/users/me", json={"name": "new_name"})
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["name"] == "new_name"
            assert resp["success"] is True
    destroy_ctfd(app)


def test_api_user_change_email():
    """Test that users can change their email via the API"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        app.db.session.commit()
        with login_as_user(app) as client:
            # Test users can't submit null
            r = client.patch(
                "/api/v1/users/me", json={"email": None, "confirm": "password"}
            )
            resp = r.get_json()
            print(resp)
            assert r.status_code == 400
            assert resp["errors"]["email"] == ["Field may not be null."]

            # Test users can exercise the API
            r = client.patch(
                "/api/v1/users/me",
                json={"email": "new_email@email.com", "confirm": "password"},
            )
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["email"] == "new_email@email.com"
            assert resp["success"] is True
            user = Users.query.filter_by(id=2).first()
            assert user.email == "new_email@email.com"
    destroy_ctfd(app)


def test_api_user_change_verify_email():
    """Test that users are marked unconfirmed if they change their email and verify_emails is turned on"""
    app = create_ctfd()
    with app.app_context():
        set_config("verify_emails", True)
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        user.verified = True
        app.db.session.commit()
        with login_as_user(app) as client:
            r = client.patch(
                "/api/v1/users/me",
                json={"email": "new_email@email.com", "confirm": "password"},
            )
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["email"] == "new_email@email.com"
            assert resp["success"] is True
            user = Users.query.filter_by(id=2).first()
            assert user.verified is False
    destroy_ctfd(app)


def test_api_user_change_email_under_whitelist():
    """Test that users can only change emails to ones in the whitelist"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        set_config(
            "domain_whitelist", "whitelisted.com, whitelisted.org, whitelisted.net"
        )
        with login_as_user(app) as client:
            r = client.patch(
                "/api/v1/users/me",
                json={"email": "new_email@email.com", "confirm": "password"},
            )
            assert r.status_code == 400
            resp = r.get_json()
            assert resp["errors"]["email"]
            assert resp["success"] is False

            r = client.patch(
                "/api/v1/users/me",
                json={"email": "new_email@whitelisted.com", "confirm": "password"},
            )
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["email"] == "new_email@whitelisted.com"
            assert resp["success"] is True
    destroy_ctfd(app)


def test_api_user_get_me_solves_not_logged_in():
    """Can a user get /api/v1/users/me/solves if not logged in"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/users/me/solves", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_get_me_solves_logged_in():
    """Can a user get /api/v1/users/me/solves if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/me/solves")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_solves():
    """Can a user get /api/v1/users/<user_id>/solves if logged in"""
    app = create_ctfd(user_mode="users")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/2/solves")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_solves_after_freze_time():
    """Can a user get /api/v1/users/<user_id>/solves after freeze time"""
    app = create_ctfd(user_mode="users")
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
            chal2 = gen_solve(app.db, user_id=2, challenge_id=chal2_id)

            # There should now be two solves assigned to the same user.
            assert Solves.query.count() == 2

            # User 2 should have 2 solves when seen by themselves
            client = login_as_user(app, name="user1")
            r = client.get("/api/v1/users/me/solves")
            data = r.get_json()["data"]
            assert len(data) == 2

            # User 2 should have 1 solve when seen by another user
            client = login_as_user(app, name="user2")
            r = client.get("/api/v1/users/2/solves")
            data = r.get_json()["data"]
            assert len(data) == 1

            # Admins should see all solves for the user
            admin = login_as_user(app, name="admin")

            r = admin.get("/api/v1/users/2/solves")
            data = r.get_json()["data"]
            assert len(data) == 2
    destroy_ctfd(app)


def test_api_user_get_me_fails_not_logged_in():
    """Can a user get /api/v1/users/me/fails if not logged in"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/users/me/fails", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_get_me_fails_logged_in():
    """Can a user get /api/v1/users/me/fails if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/me/fails")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_fails():
    """Can a user get /api/v1/users/<user_id>/fails if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/2/fails")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_fails_after_freze_time():
    """Can a user get /api/v1/users/<user_id>/fails after freeze time"""
    app = create_ctfd(user_mode="users")
    with app.app_context():
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            chal = gen_challenge(app.db)
            chal_id = chal.id
            chal2 = gen_challenge(app.db)
            chal2_id = chal2.id
            gen_fail(app.db, user_id=2, challenge_id=chal_id)

        with freeze_time("2017-10-8"):
            chal2 = gen_fail(app.db, user_id=2, challenge_id=chal2_id)

            # There should now be two fails assigned to the same user.
            assert Fails.query.count() == 2

            # User 2 should have 2 fail when seen by themselves
            client = login_as_user(app, name="user1")
            r = client.get("/api/v1/users/me/fails")
            assert r.get_json()["meta"]["count"] == 2

            # User 2 should have 1 fail when seen by another user
            client = login_as_user(app, name="user2")
            r = client.get("/api/v1/users/2/fails")
            assert r.get_json()["meta"]["count"] == 1

            # Admins should see all fails for the user
            admin = login_as_user(app, name="admin")

            r = admin.get("/api/v1/users/2/fails")
            assert r.get_json()["meta"]["count"] == 2
    destroy_ctfd(app)


def test_api_user_get_me_awards_not_logged_in():
    """Can a user get /api/v1/users/me/awards if not logged in"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/users/me/awards", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_user_get_me_awards_logged_in():
    """Can a user get /api/v1/users/me/awards if logged in"""
    app = create_ctfd(user_mode="users")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/me/awards")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_awards():
    """Can a user get /api/v1/users/<user_id>/awards if logged in"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/users/2/awards")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_user_get_awards_after_freze_time():
    """Can a user get /api/v1/users/<user_id>/awards after freeze time"""
    app = create_ctfd(user_mode="users")
    with app.app_context():
        register_user(app, name="user1", email="user1@examplectf.com")
        register_user(app, name="user2", email="user2@examplectf.com")

        # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            gen_award(app.db, user_id=2)

        with freeze_time("2017-10-8"):
            gen_award(app.db, user_id=2)

            # There should now be two awards assigned to the same user.
            assert Awards.query.count() == 2

            # User 2 should have 2 awards when seen by themselves
            client = login_as_user(app, name="user1")
            r = client.get("/api/v1/users/me/awards")
            data = r.get_json()["data"]
            assert len(data) == 2

            # User 2 should have 1 award when seen by another user
            client = login_as_user(app, name="user2")
            r = client.get("/api/v1/users/2/awards")
            data = r.get_json()["data"]
            assert len(data) == 1

            # Admins should see all awards for the user
            admin = login_as_user(app, name="admin")

            r = admin.get("/api/v1/users/2/awards")
            data = r.get_json()["data"]
            assert len(data) == 2
    destroy_ctfd(app)


def test_api_accessing_hidden_users():
    """Hidden users should not be visible to normal users, only to admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="visible_user", email="visible_user@examplectf.com")
        register_user(
            app, name="hidden_user", email="hidden_user@examplectf.com"
        )  # ID 3
        user = Users.query.filter_by(name="hidden_user").first()
        user.hidden = True
        app.db.session.commit()

        with login_as_user(app, name="visible_user") as client:
            list_users = client.get("/api/v1/users").get_json()["data"]
            assert len(list_users) == 1

            assert client.get("/api/v1/users/3").status_code == 404
            assert client.get("/api/v1/users/3/solves").status_code == 404
            assert client.get("/api/v1/users/3/fails").status_code == 404
            assert client.get("/api/v1/users/3/awards").status_code == 404

        with login_as_user(app, name="admin") as client:
            # Admins see the user in lists
            list_users = client.get("/api/v1/users?view=admin").get_json()["data"]
            assert len(list_users) == 3

            assert client.get("/api/v1/users/3").status_code == 200
            assert client.get("/api/v1/users/3/solves").status_code == 200
            assert client.get("/api/v1/users/3/fails").status_code == 200
            assert client.get("/api/v1/users/3/awards").status_code == 200
    destroy_ctfd(app)


def test_api_accessing_banned_users():
    """Banned users should not be visible to normal users, only to admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="visible_user", email="visible_user@examplectf.com")
        register_user(
            app, name="banned_user", email="banned_user@examplectf.com"
        )  # ID 3
        user = Users.query.filter_by(name="banned_user").first()
        user.banned = True
        app.db.session.commit()

        with login_as_user(app, name="visible_user") as client:
            list_users = client.get("/api/v1/users").get_json()["data"]
            assert len(list_users) == 1

            assert client.get("/api/v1/users/3").status_code == 404
            assert client.get("/api/v1/users/3/solves").status_code == 404
            assert client.get("/api/v1/users/3/fails").status_code == 404
            assert client.get("/api/v1/users/3/awards").status_code == 404

        with login_as_user(app, name="admin") as client:
            # Admins see the user in lists
            list_users = client.get("/api/v1/users?view=admin").get_json()["data"]
            assert len(list_users) == 3

            assert client.get("/api/v1/users/3").status_code == 200
            assert client.get("/api/v1/users/3/solves").status_code == 200
            assert client.get("/api/v1/users/3/fails").status_code == 200
            assert client.get("/api/v1/users/3/awards").status_code == 200
    destroy_ctfd(app)


def test_api_user_send_email():
    """Can an admin post /api/v1/users/<user_id>/email"""
    app = create_ctfd()
    with app.app_context():

        register_user(app)

        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/users/2/email", json={"text": "email should get rejected"}
            )
            assert r.status_code == 403

        with login_as_user(app, "admin") as admin:
            r = admin.post(
                "/api/v1/users/2/email", json={"text": "email should be accepted"}
            )
            assert r.get_json() == {
                "success": False,
                "errors": {"": ["Email settings not configured"]},
            }
            assert r.status_code == 400

        set_config("verify_emails", True)
        set_config("mail_server", "localhost")
        set_config("mail_port", 25)
        set_config("mail_useauth", True)
        set_config("mail_username", "username")
        set_config("mail_password", "password")

        with login_as_user(app, "admin") as admin:
            r = admin.post("/api/v1/users/2/email", json={"text": ""})
            assert r.get_json() == {
                "success": False,
                "errors": {"text": ["Email text cannot be empty"]},
            }
            assert r.status_code == 400

        with login_as_user(app, "admin") as admin:
            r = admin.post(
                "/api/v1/users/2/email", json={"text": "email should be accepted"}
            )
            # Email should go through but since we aren't mocking
            # the server we get a Connection refused error
            assert r.status_code == 400

    destroy_ctfd(app)


def test_api_user_get_schema():
    """Can a user get /api/v1/users/<user_id> doesn't return unnecessary data"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@examplectf.com")  # ID 2
        register_user(app, name="user2", email="user2@examplectf.com")  # ID 3

        with app.test_client() as client:
            r = client.get("/api/v1/users/3")
            data = r.get_json()["data"]
            assert sorted(data.keys()) == sorted(
                UserSchema.views["user"] + ["score", "place"]
            )

        with login_as_user(app, name="user1") as client:
            r = client.get("/api/v1/users/3")
            data = r.get_json()["data"]
            assert sorted(data.keys()) == sorted(
                UserSchema.views["user"] + ["score", "place"]
            )
    destroy_ctfd(app)


def test_api_user_patch_team_id():
    """Users can't patch their team_id directly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_team(app.db)

        with login_as_user(app) as client:
            data = {
                "team_id": 1,
            }
            r = client.patch("/api/v1/users/me", json=data)
            data = r.get_json()
            assert data["data"]["team_id"] is None
    destroy_ctfd(app)
