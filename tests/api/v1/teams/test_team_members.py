#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    gen_user,
    gen_team
)


def test_api_team_get_members():
    """Can a user get /api/v1/teams/<team_id>/members only if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.get('/api/v1/teams/1/members', json="")
            assert r.status_code == 403

        with login_as_user(app, name="admin") as client:
            r = client.get('/api/v1/teams/1/members', json="")
            assert r.status_code == 200

            resp = r.get_json()
            assert resp['data'] == [2]
    destroy_ctfd(app)


def test_api_team_remove_members():
    """Can a user remove /api/v1/teams/<team_id>/members only if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user1 = gen_user(app.db, name="user1", email="user1@ctfd.io")  # ID 2
        user2 = gen_user(app.db, name="user2", email="user2@ctfd.io")  # ID 3
        team = gen_team(app.db)
        team.members.append(user1)
        team.members.append(user2)
        user1.team_id = team.id
        user2.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user1") as client:
            r = client.delete('/api/v1/teams/1/members', json={
                'id': 2
            })
            assert r.status_code == 403

        with login_as_user(app, name="admin") as client:
            r = client.delete('/api/v1/teams/1/members', json={
                'id': 2
            })
            assert r.status_code == 200

            resp = r.get_json()
            assert resp['data'] == [3]

            r = client.delete('/api/v1/teams/1/members', json={
                'id': 2
            })

            resp = r.get_json()
            assert 'User is not part of this team' in resp['errors']['id']
            assert r.status_code == 400
    destroy_ctfd(app)


def test_api_admin_can_change_captain():
    """Can admins/captains change captains for teams"""
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

        # I am not the captain
        with login_as_user(app, name="user2") as client:
            r = client.patch('/api/v1/teams/1', json={
                'captain_id': 3
            })
            assert r.status_code == 403

        # Look at me, I'm the captain now
        with login_as_user(app, name="user1") as client:
            r = client.patch('/api/v1/teams/1', json={
                'captain_id': 3
            })
            # We should still receive a 403 because admins are the only people who can change captains for specific teams
            assert r.status_code == 403

        # Escalate to admin
        with login_as_user(app, name="admin") as client:
            r = client.patch('/api/v1/teams/1', json={
                'captain_id': 3
            })
            resp = r.get_json()
            assert resp['data']['captain_id'] == 3
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_users_can_change_captain_on_self_team():
    """Can admins/captains change captains for their own team"""
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

        # I am not the captain
        with login_as_user(app, name="user2") as client:
            r = client.patch('/api/v1/teams/me', json={
                'captain_id': 3
            })
            assert r.status_code == 400

        # Look at me, I'm the captain now
        with login_as_user(app, name="user1") as client:
            r = client.patch('/api/v1/teams/me', json={
                'captain_id': 3
            })
            resp = r.get_json()
            assert resp['data']['captain_id'] == 3
            assert r.status_code == 200
    destroy_ctfd(app)
