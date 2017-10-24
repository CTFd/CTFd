#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import Teams, Challenges
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended
from freezegun import freeze_time
from mock import patch


def test_admin_panel():
    """Does the admin panel return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin')
        assert r.status_code == 302
        r = client.get('/admin/graphs')
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
                'desc': 'description',
                'value': 100,
                'key_type[0]': 'static',
                'max_attempts': '',
                'nonce': sess.get('nonce'),
                'chaltype': 'standard'
            }
            r = client.post('/admin/chal/new', data=data)

        assert Challenges.query.count() == 1
    destroy_ctfd(app)


def test_admins_can_update_challenges():
    '''Test that admins can create new challenges'''
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
                'desc': 'description',
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
