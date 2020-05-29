#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time

from CTFd.models import Awards, Fails, Solves, Teams, Users
from CTFd.utils import set_config
from CTFd.utils.crypto import verify_password
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_fail,
    gen_flag,
    gen_solve,
    gen_team,
    gen_user,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_api_teams_get_public():
    """Can a user get /api/v1/teams if teams are public"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_teams_get_private():
    """Can a user get /api/v1/teams if teams are private"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_teams_get_admin():
    """Can a user get /api/v1/teams if teams are viewed by admins only"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, "admin") as client:
            set_config("account_visibility", "public")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_teams_post_non_admin():
    """Can a user post /api/v1/teams if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.post("/api/v1/teams", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_teams_post_admin():
    """Can a user post /api/v1/teams if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, "admin") as client:
            # Create team
            r = client.post(
                "/api/v1/teams",
                json={
                    "website": "http://www.team.com",
                    "name": "team",
                    "country": "TW",
                    "email": "team@team.com",
                    "affiliation": "team",
                    "password": "password",
                },
            )
            assert r.status_code == 200

            # Make sure password was hashed properly
            team = Teams.query.filter_by(email="team@team.com").first()
            assert team
            assert verify_password("password", team.password)

            # Make sure team can actually be joined
            register_user(app)
            client = login_as_user(app)

            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/teams/join", data=data)
            user = Users.query.filter_by(id=2).first()
            assert user.team_id == 1
    destroy_ctfd(app)


def test_api_teams_post_admin_duplicate():
    """Test that admins can only create teams with unique information"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db, name="team1")
        with login_as_user(app, "admin") as client:
            # Duplicate name
            r = client.post(
                "/api/v1/teams",
                json={
                    "website": "https://ctfd.io",
                    "name": "team1",
                    "country": "TW",
                    "email": "team1@ctfd.io",
                    "affiliation": "team",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["name"]
            assert resp["success"] is False
            assert Teams.query.count() == 1

            # Duplicate email
            r = client.post(
                "/api/v1/teams",
                json={
                    "website": "https://ctfd.io",
                    "name": "new_team",
                    "country": "TW",
                    "email": "team@ctfd.io",
                    "affiliation": "team",
                    "password": "password",
                },
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["email"]
            assert resp["success"] is False
            assert Teams.query.count() == 1
    destroy_ctfd(app)


def test_api_team_get_public():
    """Can a user get /api/v1/team/<team_id> if teams are public"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            set_config("account_visibility", "public")
            gen_team(app.db)
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 302
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_private():
    """Can a user get /api/v1/teams/<team_id> if teams are private"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            set_config("account_visibility", "public")
            gen_team(app.db)
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_admin():
    """Can a user get /api/v1/teams/<team_id> if teams are viewed by admins only"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, "admin") as client:
            gen_team(app.db)
            set_config("account_visibility", "public")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
            set_config("account_visibility", "private")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
            set_config("account_visibility", "admins")
            r = client.get("/api/v1/teams/1")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_patch_non_admin():
    """Can a user patch /api/v1/teams/<team_id> if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with app.test_client() as client:
            r = client.patch("/api/v1/teams/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_patch_admin():
    """Can a user patch /api/v1/teams/<team_id> if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with login_as_user(app, "admin") as client:
            r = client.patch(
                "/api/v1/teams/1",
                json={
                    "name": "team_name",
                    "email": "team@ctfd.io",
                    "password": "password",
                    "affiliation": "changed",
                },
            )
            team = Teams.query.filter_by(id=1).first()
            assert r.status_code == 200
            assert r.get_json()["data"]["affiliation"] == "changed"
            assert verify_password("password", team.password)
    destroy_ctfd(app)


def test_api_team_delete_non_admin():
    """Can a user delete /api/v1/teams/<team_id> if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with app.test_client() as client:
            r = client.delete("/api/v1/teams/1", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_delete_admin():
    """Can a user patch /api/v1/teams/<team_id> if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team = gen_team(app.db)

        assert len(team.members) == 4

        members = team.members
        for user in members:
            simulate_user_activity(app.db, user=user)

        with login_as_user(app, "admin") as client:
            r = client.delete("/api/v1/teams/1", json="")
            assert r.status_code == 200
            assert r.get_json().get("data") is None

        for user in Users.query.all():
            assert user.team_id is None
    destroy_ctfd(app)


def test_api_team_get_me_not_logged_in():
    """Can a user get /api/v1/teams/me if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/teams/me")
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_team_get_me_logged_in():
    """Can a user get /api/v1/teams/me if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/me")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_patch_me_not_logged_in():
    """Can a user patch /api/v1/teams/me if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.patch("/api/v1/teams/me", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_patch_me_logged_in_user():
    """Can a user patch /api/v1/teams/me if logged in as a regular user"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user1 = gen_user(app.db, name="user1", email="user1@ctfd.io")
        user2 = gen_user(app.db, name="user2", email="user2@ctfd.io")
        team = gen_team(app.db)
        team.members.append(user1)
        team.members.append(user2)
        user1.team_id = team.id
        user2.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user2") as client:
            r = client.patch(
                "/api/v1/teams/me", json={"name": "team_name", "affiliation": "changed"}
            )
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_patch_me_logged_in_captain():
    """Can a user patch /api/v1/teams/me if logged in as the captain"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        team.captain_id = 2
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.patch(
                "/api/v1/teams/me", json={"name": "team_name", "affiliation": "changed"}
            )
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_patch_me_logged_in_admin_captain():
    """Can an admin patch /api/v1/teams/me if logged in as a team captain"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        admin = Users.query.filter_by(id=1).first()
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        team.members.append(admin)

        user.team_id = team.id
        admin.team_id = team.id

        # We want the admin to be the captain
        team.captain_id = 1

        app.db.session.commit()
        with login_as_user(app, name="admin") as client:
            # Users can't null out their team name
            r = client.patch("/api/v1/teams/me", json={"name": None})
            resp = r.get_json()
            assert r.status_code == 400
            assert resp["errors"]["name"] == ["Field may not be null."]

            r = client.patch(
                "/api/v1/teams/me", json={"name": "team_name", "affiliation": "changed"}
            )
            assert r.status_code == 200

        team = Teams.query.filter_by(id=1).first()
        assert team.name == "team_name"
    destroy_ctfd(app)


def test_api_team_get_me_solves_not_logged_in():
    """Can a user get /api/v1/teams/me/solves if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/teams/me/solves", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_get_me_solves_logged_in():
    """Can a user get /api/v1/teams/me/solves if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/me/solves")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_solves():
    """Can a user get /api/v1/teams/<team_id>/solves if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/1/solves")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_solves_after_freze_time():
    """Can a user get /api/v1/teams/<team_id>/solves after freeze time"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db, name="team1", email="team1@ctfd.io", member_count=1)

        team_member = team.members[0]
        tm_name = team_member.name

        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_solve(app.db, user_id=3, team_id=1, challenge_id=chal_id)
            chal2 = gen_challenge(app.db)
            chal2_id = chal2.id

        with freeze_time("2017-10-8"):
            gen_solve(app.db, user_id=3, team_id=1, challenge_id=chal2_id)

            assert Solves.query.count() == 2

            with login_as_user(app) as client:
                r = client.get("/api/v1/teams/1/solves")
                data = r.get_json()["data"]
                assert len(data) == 1

            with login_as_user(app, name=tm_name) as client:
                r = client.get("/api/v1/teams/me/solves")
                data = r.get_json()["data"]
                assert len(data) == 2

            with login_as_user(app, name="admin") as client:
                r = client.get("/api/v1/teams/1/solves")
                data = r.get_json()["data"]
                assert len(data) == 2
    destroy_ctfd(app)


def test_api_team_get_me_fails_not_logged_in():
    """Can a user get /api/v1/teams/me/fails if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/teams/me/fails", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_get_me_fails_logged_in():
    """Can a user get /api/v1/teams/me/fails if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/me/fails")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_fails():
    """Can a user get /api/v1/teams/<team_id>/fails if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/1/fails")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_fails_after_freze_time():
    """Can a user get /api/v1/teams/<team_id>/fails after freeze time"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db, name="team1", email="team1@ctfd.io", member_count=1)

        team_member = team.members[0]
        tm_name = team_member.name

        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            chal = gen_challenge(app.db)
            chal_id = chal.id
            chal2 = gen_challenge(app.db)
            chal2_id = chal2.id
            gen_fail(app.db, user_id=3, team_id=1, challenge_id=chal_id)

        with freeze_time("2017-10-8"):
            gen_fail(app.db, user_id=3, team_id=1, challenge_id=chal2_id)

            assert Fails.query.count() == 2

            with login_as_user(app) as client:
                r = client.get("/api/v1/teams/1/fails")
                assert r.get_json()["meta"]["count"] == 1

            with login_as_user(app, name=tm_name) as client:
                r = client.get("/api/v1/teams/me/fails")
                assert r.get_json()["meta"]["count"] == 2

            with login_as_user(app, name="admin") as client:
                r = client.get("/api/v1/teams/1/fails")
                assert r.get_json()["meta"]["count"] == 2
    destroy_ctfd(app)


def test_api_team_get_me_awards_not_logged_in():
    """Can a user get /api/v1/teams/me/awards if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/teams/me/awards", json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_get_me_awards_logged_in():
    """Can a user get /api/v1/teams/me/awards if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/me/awards")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_awards():
    """Can a user get /api/v1/teams/<team_id>/awards if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/1/awards")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_awards_after_freze_time():
    """Can a user get /api/v1/teams/<team_id>/awards after freeze time"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db, name="team1", email="team1@ctfd.io", member_count=1)

        team_member = team.members[0]
        tm_name = team_member.name

        set_config("freeze", "1507262400")
        with freeze_time("2017-10-4"):
            gen_award(app.db, user_id=3)

        with freeze_time("2017-10-8"):
            gen_award(app.db, user_id=3)

            assert Awards.query.count() == 2

            with login_as_user(app) as client:
                r = client.get("/api/v1/teams/1/awards")
                data = r.get_json()["data"]
                assert len(data) == 1

            with login_as_user(app, name=tm_name) as client:
                r = client.get("/api/v1/teams/me/awards")
                data = r.get_json()["data"]
                assert len(data) == 2

            with login_as_user(app, name="admin") as client:
                r = client.get("/api/v1/teams/1/awards")
                data = r.get_json()["data"]
                assert len(data) == 2
    destroy_ctfd(app)


def test_api_team_patch_password():
    """Can a user change their team password /api/v1/teams/me if logged in as the captain"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user1 = gen_user(app.db, name="user1", email="user1@ctfd.io")  # ID 2
        user2 = gen_user(app.db, name="user2", email="user2@ctfd.io")  # ID 3
        team = gen_team(app.db)
        team.members.append(user1)
        team.members.append(user2)
        team.captain_id = 2
        user1.team_id = team.id
        user2.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user2") as client:
            r = client.patch(
                "/api/v1/teams/me",
                json={"confirm": "password", "password": "new_password"},
            )
            assert r.status_code == 403

            assert r.get_json() == {
                "errors": {"": ["Only team captains can edit team information"]},
                "success": False,
            }

            team = Teams.query.filter_by(id=1).first()
            assert (
                verify_password(plaintext="new_password", ciphertext=team.password)
                is False
            )

        with login_as_user(app, name="user1") as client:
            r = client.patch(
                "/api/v1/teams/me",
                json={"confirm": "password", "password": "new_password"},
            )
            assert r.status_code == 200

            team = Teams.query.filter_by(id=1).first()
            assert verify_password(plaintext="new_password", ciphertext=team.password)


def test_api_accessing_hidden_banned_users():
    """Hidden/Banned users should not be visible to normal users, only to admins"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        register_user(app, name="user2", email="user2@ctfd.io")
        register_user(app, name="visible_user", email="visible_user@ctfd.io")

        user = Users.query.filter_by(id=2).first()
        team = gen_team(
            app.db, name="hidden_team", email="hidden_team@ctfd.io", hidden=True
        )
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()

        user = Users.query.filter_by(id=3).first()
        team = gen_team(
            app.db, name="banned_team", email="banned_team@ctfd.io", banned=True
        )
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()

        with login_as_user(app, name="visible_user") as client:
            list_teams = client.get("/api/v1/teams").get_json()["data"]
            assert len(list_teams) == 0

            assert client.get("/api/v1/teams/1").status_code == 404
            assert client.get("/api/v1/teams/1/solves").status_code == 404
            assert client.get("/api/v1/teams/1/fails").status_code == 404
            assert client.get("/api/v1/teams/1/awards").status_code == 404

            assert client.get("/api/v1/teams/2").status_code == 404
            assert client.get("/api/v1/teams/2/solves").status_code == 404
            assert client.get("/api/v1/teams/2/fails").status_code == 404
            assert client.get("/api/v1/teams/2/awards").status_code == 404

        with login_as_user(app, name="admin") as client:
            # Admins see hidden teams in lists
            list_users = client.get("/api/v1/teams?view=admin").get_json()["data"]
            assert len(list_users) == 2

            assert client.get("/api/v1/teams/1").status_code == 200
            assert client.get("/api/v1/teams/1/solves").status_code == 200
            assert client.get("/api/v1/teams/1/fails").status_code == 200
            assert client.get("/api/v1/teams/1/awards").status_code == 200

            assert client.get("/api/v1/teams/2").status_code == 200
            assert client.get("/api/v1/teams/2/solves").status_code == 200
            assert client.get("/api/v1/teams/2/fails").status_code == 200
            assert client.get("/api/v1/teams/2/awards").status_code == 200
    destroy_ctfd(app)


def test_api_user_without_team_challenge_interaction():
    """Can a user interact with challenges without having joined a team?"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        gen_challenge(app.db)
        gen_flag(app.db, 1)

        with login_as_user(app) as client:
            assert client.get("/api/v1/challenges").status_code == 403
            assert client.get("/api/v1/challenges/1").status_code == 403
            assert (
                client.post(
                    "/api/v1/challenges/attempt",
                    json={"challenge_id": 1, "submission": "wrong_flag"},
                ).status_code
                == 403
            )

        # Create a user with a team
        user = gen_user(app.db, email="user_name@ctfd.io")
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()

        # Test if user with team can interact with challenges
        with login_as_user(app, name="user_name") as client:
            assert client.get("/api/v1/challenges").status_code == 200
            assert client.get("/api/v1/challenges/1").status_code == 200
            assert (
                client.post(
                    "/api/v1/challenges/attempt",
                    json={"challenge_id": 1, "submission": "flag"},
                ).status_code
                == 200
            )
    destroy_ctfd(app)
