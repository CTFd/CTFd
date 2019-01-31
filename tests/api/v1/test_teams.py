#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from CTFd.utils.crypto import verify_password
from tests.helpers import *


def test_api_teams_get_public():
    """Can a user get /api/v1/teams if teams are public"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            set_config('account_visibility', 'public')
            r = client.get('/api/v1/teams')
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams')
            assert r.status_code == 302
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_teams_get_private():
    """Can a user get /api/v1/teams if teams are private"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            set_config('account_visibility', 'public')
            r = client.get('/api/v1/teams')
            print(r.__dict__)
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams')
            assert r.status_code == 200
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_teams_get_admin():
    """Can a user get /api/v1/teams if teams are viewed by admins only"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            set_config('account_visibility', 'public')
            r = client.get('/api/v1/teams')
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams')
            assert r.status_code == 200
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_teams_post_non_admin():
    """Can a user post /api/v1/teams if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.post('/api/v1/teams', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_teams_post_admin():
    """Can a user post /api/v1/teams if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            # Create team
            r = client.post(
                '/api/v1/teams',
                json={
                    "website": "http://www.team.com",
                    "name": "team",
                    "country": "TW",
                    "email": "team@team.com",
                    "affiliation": "team",
                    "password": "password"
                }
            )
            assert r.status_code == 200

            # Make sure password was hashed properly
            team = Teams.query.filter_by(email='team@team.com').first()
            assert team
            assert verify_password('password', team.password)

            # Make sure team can actually be joined
            register_user(app)
            client = login_as_user(app)

            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get('nonce')
                }
            r = client.post('/teams/join', data=data)
            user = Users.query.filter_by(id=2).first()
            assert user.team_id == 1
    destroy_ctfd(app)


def test_api_teams_post_admin_duplicate():
    """Test that admins can only create teams with unique information"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db, name='team1')
        with login_as_user(app, 'admin') as client:
            # Duplicate name
            r = client.post(
                '/api/v1/teams',
                json={
                    "website": "https://ctfd.io",
                    "name": "team1",
                    "country": "TW",
                    "email": "team1@ctfd.io",
                    "affiliation": "team",
                    "password": "password"
                }
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp['errors']['name']
            assert resp['success'] is False
            assert Teams.query.count() == 1

            # Duplicate email
            r = client.post(
                '/api/v1/teams',
                json={
                    "website": "https://ctfd.io",
                    "name": "new_team",
                    "country": "TW",
                    "email": "team@ctfd.io",
                    "affiliation": "team",
                    "password": "password"
                }
            )
            resp = r.get_json()
            assert r.status_code == 400
            assert resp['errors']['email']
            assert resp['success'] is False
            assert Teams.query.count() == 1
    destroy_ctfd(app)


def test_api_team_get_public():
    """Can a user get /api/v1/team/<team_id> if teams are public"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            set_config('account_visibility', 'public')
            gen_team(app.db)
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 302
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_private():
    """Can a user get /api/v1/teams/<team_id> if teams are private"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            set_config('account_visibility', 'public')
            gen_team(app.db)
            r = client.get('/api/v1/teams/1')
            print(r.__dict__)
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 200
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_team_get_admin():
    """Can a user get /api/v1/teams/<team_id> if teams are viewed by admins only"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            gen_team(app.db)
            set_config('account_visibility', 'public')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 200
            set_config('account_visibility', 'admins')
            r = client.get('/api/v1/teams/1')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_patch_non_admin():
    """Can a user patch /api/v1/teams/<team_id> if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with app.test_client() as client:
            r = client.patch('/api/v1/teams/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_patch_admin():
    """Can a user patch /api/v1/teams/<team_id> if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.patch('/api/v1/teams/1', json={
                "name": "team_name",
                "email": "team@ctfd.io",
                "password": "password",
                "affiliation": "changed"
            })
            team = Teams.query.filter_by(id=1).first()
            assert r.status_code == 200
            assert r.get_json()['data']['affiliation'] == 'changed'
            assert verify_password('password', team.password)
    destroy_ctfd(app)


def test_api_team_delete_non_admin():
    """Can a user delete /api/v1/teams/<team_id> if not admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with app.test_client() as client:
            r = client.delete('/api/v1/teams/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_delete_admin():
    """Can a user patch /api/v1/teams/<team_id> if admin"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_team(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.delete('/api/v1/teams/1', json="")
            assert r.status_code == 200
            assert r.get_json().get('data') is None
    destroy_ctfd(app)


def test_api_team_get_me_not_logged_in():
    """Can a user get /api/v1/teams/me if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/teams/me')
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
            r = client.get('/api/v1/teams/me')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_patch_me_not_logged_in():
    """Can a user patch /api/v1/teams/me if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.patch('/api/v1/teams/me', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_team_patch_me_logged_in():
    """Can a user patch /api/v1/teams/me if logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            r = client.patch('/api/v1/teams/me', json={"name": "team_name", "affiliation": "changed"})
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_me_solves_not_logged_in():
    """Can a user get /api/v1/teams/me/solves if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/teams/me/solves')
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
            r = client.get('/api/v1/teams/me/solves')
            print(r.get_json())
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
            r = client.get('/api/v1/teams/1/solves')
            print(r.get_json())
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_me_fails_not_logged_in():
    """Can a user get /api/v1/teams/me/fails if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/teams/me/fails')
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
            r = client.get('/api/v1/teams/me/fails')
            print(r.get_json())
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
            r = client.get('/api/v1/teams/1/fails')
            print(r.get_json())
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_team_get_me_awards_not_logged_in():
    """Can a user get /api/v1/teams/me/awards if not logged in"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/teams/me/awards')
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
            r = client.get('/api/v1/teams/me/awards')
            print(r.get_json())
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
            r = client.get('/api/v1/teams/1/awards')
            print(r.get_json())
            assert r.status_code == 200
    destroy_ctfd(app)
