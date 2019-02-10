#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from tests.helpers import *


def test_teams_get():
    """Can a user get /teams"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        with app.test_client() as client:
            set_config('account_visibility', 'public')
            r = client.get('/teams')
            assert r.status_code == 200
            set_config('account_visibility', 'private')
            r = client.get('/teams')
            assert r.status_code == 302
            set_config('account_visibility', 'admins')
            r = client.get('/teams')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_hidden_teams_visibility():
    """Hidden teams should not show up on /teams or /api/v1/teams or /api/v1/scoreboard"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            user = Users.query.filter_by(id=2).first()
            team = gen_team(app.db, name='visible_team', hidden=True)
            team.members.append(user)
            user.team_id = team.id
            app.db.session.commit()

            r = client.get('/teams')
            response = r.get_data(as_text=True)
            assert team.name not in response

            r = client.get('/api/v1/teams')
            response = r.get_json()
            assert team.name not in response

            gen_award(app.db, user.id, team_id=team.id)

            r = client.get('/scoreboard')
            response = r.get_data(as_text=True)
            assert team.name not in response

            r = client.get('/api/v1/scoreboard')
            response = r.get_json()
            assert team.name not in response

            # Team should re-appear after disabling hiding
            # Use an API call to cause a cache clear
            with login_as_user(app, name='admin') as admin:
                r = admin.patch('/api/v1/teams/1', json={
                    "hidden": False,
                })
                assert r.status_code == 200

            r = client.get('/teams')
            response = r.get_data(as_text=True)
            assert team.name in response

            r = client.get('/api/v1/teams')
            response = r.get_data(as_text=True)
            assert team.name in response

            r = client.get('/api/v1/scoreboard')
            response = r.get_data(as_text=True)
            assert team.name in response
    destroy_ctfd(app)


def test_teams_get_user_mode():
    """Can a user get /teams if user mode"""
    app = create_ctfd(user_mode="users")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get('/teams')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_teams_new_get():
    """Can a user get /teams/new"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            r = client.get('/teams/new')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_teams_new_post():
    """Can a user post /teams/new"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_user(app.db, name="user")
        with login_as_user(app) as client:
            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get('nonce')
                }
            r = client.post('/teams/new', data=data)
            assert r.status_code == 302
            r = client.post('/teams/new', data=data)
            assert r.status_code == 200
            incorrect_data = data
            incorrect_data['name'] = ''
            r = client.post('/teams/new', data=incorrect_data)
            assert r.status_code == 200
    destroy_ctfd(app)


def test_team_get():
    """Can a user get /team"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name", password="password") as client:
            r = client.get('/team')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_teams_id_get():
    """Can a user get /teams/<int:team_id>"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        team = gen_team(app.db)
        team.members.append(user)
        user.team_id = team.id
        app.db.session.commit()
        with login_as_user(app, name="user_name", password="password") as client:
            r = client.get('/teams/1')
            assert r.status_code == 200
    destroy_ctfd(app)
