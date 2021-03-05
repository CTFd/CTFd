#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Awards, Solves, Submissions, Unlocks, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_team,
    gen_user,
    login_as_user,
    simulate_user_activity,
)


def test_api_team_get_members():
    """Can a user get /api/v1/teams/<team_id>/members only if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        app.db.session.commit()

        gen_user(app.db, name="user_name")
        with login_as_user(app, name="user_name") as client:
            r = client.get("/api/v1/teams/1/members", json="")
            assert r.status_code == 403

        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/teams/1/members", json="")
            assert r.status_code == 200

            resp = r.get_json()
            # The following data is sorted b/c in Postgres data isn't necessarily returned ordered.
            assert sorted(resp["data"]) == sorted([2, 3, 4, 5])
    destroy_ctfd(app)


def test_api_team_remove_members():
    """Can a user remove /api/v1/teams/<team_id>/members only if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team = gen_team(app.db)
        assert len(team.members) == 4
        app.db.session.commit()

        gen_user(app.db, name="user1")
        with login_as_user(app, name="user1") as client:
            r = client.delete("/api/v1/teams/1/members", json={"user_id": 2})
            assert r.status_code == 403

        with login_as_user(app, name="admin") as client:
            r = client.delete("/api/v1/teams/1/members", json={"user_id": 2})
            assert r.status_code == 200

            resp = r.get_json()
            # The following data is sorted b/c in Postgres data isn't necessarily returned ordered.
            assert sorted(resp["data"]) == sorted([3, 4, 5])

            r = client.delete("/api/v1/teams/1/members", json={"user_id": 2})

            resp = r.get_json()
            assert "User is not part of this team" in resp["errors"]["id"]
            assert r.status_code == 400
    destroy_ctfd(app)


def test_api_removing_members_deletes_information():
    """If an admin removes a user, their score information should also be removed"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team = gen_team(app.db)
        assert len(team.members) == 4
        app.db.session.commit()

        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user)
        assert Solves.query.filter_by(user_id=2).count() == 1
        assert Submissions.query.filter_by(user_id=2).count() == 6
        assert Awards.query.filter_by(user_id=2).count() == 1
        assert Unlocks.query.filter_by(user_id=2).count() == 1

        with login_as_user(app, name="admin") as client:
            r = client.delete("/api/v1/teams/1/members", json={"user_id": 2})
            assert r.status_code == 200

        user = Users.query.filter_by(id=2).first()
        assert Solves.query.filter_by(user_id=2).count() == 0
        assert Submissions.query.filter_by(user_id=2).count() == 0
        assert Awards.query.filter_by(user_id=2).count() == 0
        assert Unlocks.query.filter_by(user_id=2).count() == 0
    destroy_ctfd(app)


def test_api_admin_can_change_captain():
    """Can admins/captains change captains for teams"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user1 = gen_user(app.db, name="user1", email="user1@examplectf.com")  # ID 2
        user2 = gen_user(app.db, name="user2", email="user2@examplectf.com")  # ID 3
        team = gen_team(app.db)
        team.members.append(user1)
        team.members.append(user2)
        team.captain_id = 2
        user1.team_id = team.id
        user2.team_id = team.id
        app.db.session.commit()

        # I am not the captain
        with login_as_user(app, name="user2") as client:
            r = client.patch("/api/v1/teams/1", json={"captain_id": 3})
            assert r.status_code == 403

        # Look at me, I'm the captain now
        with login_as_user(app, name="user1") as client:
            r = client.patch("/api/v1/teams/1", json={"captain_id": 3})
            # We should still receive a 403 because admins are the only people who can change captains for specific teams
            assert r.status_code == 403

        # Escalate to admin
        with login_as_user(app, name="admin") as client:
            r = client.patch("/api/v1/teams/1", json={"captain_id": 3})
            resp = r.get_json()
            assert resp["data"]["captain_id"] == 3
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_users_can_change_captain_on_self_team():
    """Can admins/captains change captains for their own team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user1 = gen_user(app.db, name="user1", email="user1@examplectf.com")  # ID 2
        user2 = gen_user(app.db, name="user2", email="user2@examplectf.com")  # ID 3
        team = gen_team(app.db)
        team.members.append(user1)
        team.members.append(user2)
        team.captain_id = 2
        user1.team_id = team.id
        user2.team_id = team.id
        app.db.session.commit()

        # I am not the captain
        with login_as_user(app, name="user2") as client:
            r = client.patch("/api/v1/teams/me", json={"captain_id": 3})
            assert r.status_code == 403

        # Look at me, I'm the captain now
        with login_as_user(app, name="user1") as client:
            r = client.patch("/api/v1/teams/me", json={"captain_id": 3})
            resp = r.get_json()
            assert resp["data"]["captain_id"] == 3
            assert r.status_code == 200
    destroy_ctfd(app)
