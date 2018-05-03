#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import Teams, Challenges
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended
from CTFd.plugins.challenges import get_chal_class
from freezegun import freeze_time
from mock import patch

import json


def test_admin_panel():
    """Does the admin panel return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin')
        assert r.status_code == 302
        r = client.get('/admin/statistics')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_pages():
    """Does admin pages return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_teams():
    """Does admin teams return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/teams')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_scoreboard():
    """Does admin scoreboard return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_chals():
    """Does admin chals return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_statistics():
    """Does admin statistics return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/statistics')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_config():
    """Does admin config return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/config')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admins_can_access_challenges_before_ctftime():
    '''Admins can see and solve challenges despite it being before ctftime'''
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-2"):
            client = login_as_user(app, name='admin', password='password')

            r = client.get('/challenges')
            assert r.status_code == 200
            assert "has not started" in r.get_data(as_text=True)

            r = client.get('/chals')
            assert r.status_code == 200

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 1
    destroy_ctfd(app)


def test_admins_can_create_challenges():
    '''Test that admins can create new challenges'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': '💫',
                'category': '💫',
                'description': 'description',
                'value': 100,
                'key_type[0]': 'static',
                'key': 'flag',
                'max_attempts': 5,
                'nonce': sess.get('nonce'),
                'chaltype': 'standard'
            }
            r = client.post('/admin/chal/new', data=data)
            assert r.status_code == 302

        assert Challenges.query.count() == 1
        chal = Challenges.query.filter_by(id=1).first()
        assert chal.name == '💫'
        assert chal.category == '💫'
        assert chal.max_attempts == 5
        assert chal.description == 'description'
        assert chal.value == 100
        assert chal.type == 'standard'

        assert Keys.query.count() == 1
        key = Keys.query.filter_by(id=1).first()
        assert key.type == 'static'
        assert key.flag == 'flag'
    destroy_ctfd(app)


def test_admins_can_update_challenges():
    '''Test that admins can update challenges'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        chal = gen_challenge(app.db)
        chal_id = chal.id

        assert Challenges.query.count() == 1

        with client.session_transaction() as sess:
            data = {
                'id': chal_id,
                'name': '💫',
                'category': '💫',
                'description': 'description',
                'value': 100,
                'key_type[0]': 'static',
                'max_attempts': '',
                'nonce': sess.get('nonce'),
                'chaltype': 'standard'
            }
            r = client.post('/admin/chal/update', data=data)

        assert Challenges.query.count() == 1
        chal_check = Challenges.query.filter_by(id=chal_id).first()
        assert chal_check.name == '💫'
    destroy_ctfd(app)


def test_admins_can_delete_challenges():
    '''Test that admins can delete challenges'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        chal = gen_challenge(app.db)
        chal_id = chal.id

        assert Challenges.query.count() == 1

        with client.session_transaction() as sess:
            data = {
                'id': chal_id,
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/chal/delete', data=data)
            assert r.get_data(as_text=True) == '1'

        assert Challenges.query.count() == 0
    destroy_ctfd(app)


def test_admins_can_delete_challenges_with_extras():
    """Test that admins can delete challenges that have a hint"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        chal = gen_challenge(app.db)
        chal_id = chal.id

        hint = gen_hint(app.db, chal_id)

        assert Challenges.query.count() == 1

        with client.session_transaction() as sess:
            data = {
                'id': chal_id,
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/chal/delete', data=data)
            assert r.get_data(as_text=True) == '1'

        assert Challenges.query.count() == 0
    destroy_ctfd(app)


def test_admin_chal_detail_returns_proper_data():
    """Test that the /admin/chals/<int:chalid> endpoint returns the proper data"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        chal = gen_challenge(app.db)
        tag = gen_tag(app.db, chal.id, 'test-tag')
        hint = gen_hint(app.db, chal.id, 'test-hint', 5)
        f = gen_file(app.db, chal.id, '0bf1a55a5cd327c07af15df260979668/bird.swf')

        chal_class = get_chal_class(chal.type)
        data = {
            'id': chal.id,
            'name': chal.name,
            'value': chal.value,
            'description': chal.description,
            'category': chal.category,
            'files': ['0bf1a55a5cd327c07af15df260979668/bird.swf'],
            'tags': ['test-tag'],
            'hints': [{'id': 1, 'cost': 5, 'hint': 'test-hint'}],
            'hidden': chal.hidden,
            'max_attempts': chal.max_attempts,
            'type': chal.type,
            'type_data': {
                'id': chal_class.id,
                'name': chal_class.name,
                'templates': chal_class.templates,
                'scripts': chal_class.scripts,
            }
        }

        assert Challenges.query.count() == 1

        r = client.get('/admin/chal/1')
        response = json.loads(r.get_data(as_text=True))

        assert data == response

    destroy_ctfd(app)


def test_admin_load_chal_solves():
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        gen_solve(app.db, teamid=1, chalid=chal1_id)

        r = client.get('/admin/chal/1/solves')
        data = r.get_data(as_text=True)
        assert json.loads(data)

    destroy_ctfd(app)


def test_admins_can_create_teams():
    '''Test that admins can create new teams'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': 'TunnelBunnies',
                'password': 'fUnn3lJuNK135',
                'email': 'scary.hares@trace.us',
                'website': 'https://scary-hares.trace.us/',
                'affiliation': 'Energizer',
                'country': 'USA',
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/team/new', data=data)
            assert r.status_code == 200

        team = Teams.query.filter_by(id=2).first()
        assert team
        assert team.name == 'TunnelBunnies'
        assert team.email == 'scary.hares@trace.us'
        assert team.website == 'https://scary-hares.trace.us/'
        assert team.affiliation == 'Energizer'
        assert team.country == 'USA'
    destroy_ctfd(app)


def test_admin_create_team_without_required_fields():
    '''Test that an admin can't create a new team without the required fields'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': '',
                'password': '',
                'email': '',
                'website': '',
                'affiliation': '',
                'country': '',
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/team/new', data=data)
            assert r.status_code == 200

        response = json.loads(r.get_data(as_text=True))
        assert 'data' in response
        assert len(response['data']) == 3
        assert 'The team requires a name' in response['data']
        assert 'The team requires an email' in response['data']
        assert 'The team requires a password' in response['data']
    destroy_ctfd(app)


def test_admin_create_team_with_existing_name():
    '''Test that an admin can't create a new team with an existing name'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': 'admin',
                'password': 'fUnn3lJuNK135',
                'email': 'scary.hares@trace.us',
                'website': 'https://scary-hares.trace.us/',
                'affiliation': 'Energizer',
                'country': 'USA',
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/team/new', data=data)
            assert r.status_code == 200

        response = json.loads(r.get_data(as_text=True))
        assert 'data' in response
        assert len(response['data']) == 1
        assert 'That name is taken' in response['data']
    destroy_ctfd(app)


def test_admin_create_team_with_existing_email():
    '''Test that an admin can't create a new team with an existing email'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': 'TunnelBunnies',
                'password': 'fUnn3lJuNK135',
                'email': 'admin@ctfd.io',
                'website': 'https://scary-hares.trace.us/',
                'affiliation': 'Energizer',
                'country': 'USA',
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/team/new', data=data)
            assert r.status_code == 200

        response = json.loads(r.get_data(as_text=True))
        assert 'data' in response
        assert len(response['data']) == 1
        assert 'That email is taken' in response['data']
    destroy_ctfd(app)


def test_admin_create_team_with_invalid_website():
    '''Test that an admin can't create a new team with an invalid website'''
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'name': 'TunnelBunnies',
                'password': 'fUnn3lJuNK135',
                'email': 'scary.hares@trace.us',
                'website': 'ftp://scary-hares.trace.us/',
                'affiliation': 'Energizer',
                'country': 'USA',
                'nonce': sess.get('nonce'),
            }
            r = client.post('/admin/team/new', data=data)
            assert r.status_code == 200

        response = json.loads(r.get_data(as_text=True))
        assert 'data' in response
        assert len(response['data']) == 1
        assert 'Websites must start with http:// or https://' in response['data']
    destroy_ctfd(app)
