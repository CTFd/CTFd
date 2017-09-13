#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_user_get_challenges():
    """Can a registered user load /challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_chals():
    """Can a registered user load /chals"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_viewing_challenges():
    """Test that users can see added challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get('/chals')
        chals = json.loads(r.get_data(as_text=True))
        assert len(chals['game']) == 1
    destroy_ctfd(app)


def test_chals_solves():
    '''Test that the /chals/solves endpoint works properly'''
    app = create_ctfd()
    with app.app_context():
        # Generate 5 users
        for c in range(1, 6):
            name = "user{}".format(c)
            email = "user{}@ctfd.io".format(c)
            register_user(app, name=name, email=email, password="password")

        # Generate 5 challenges
        for c in range(5):
            chal1 = gen_challenge(app.db, value=100)

        user_ids = list(range(2, 7))
        chal_ids = list(range(1, 6))
        for u in user_ids:
            for c in chal_ids:
                gen_solve(app.db, teamid=u, chalid=c)
            chal_ids.pop()

        client = login_as_user(app, name="user1")

        with client.session_transaction() as sess:
            r = client.get('/chals/solves')
            output = r.get_data(as_text=True)
            saved = json.loads('''{
              "1": 5,
              "2": 4,
              "3": 3,
              "4": 2,
              "5": 1
            }
            ''')
            received = json.loads(output)
            assert saved == received
    destroy_ctfd(app)


def test_submitting_correct_flag():
    """Test that correct flags are correct"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_incorrect_flag():
    """Test that incorrect flags are incorrect"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'notflag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
    destroy_ctfd(app)


def test_submitting_unicode_flag():
    """Test that users can submit a unicode flag"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag=u'你好')
        with client.session_transaction() as sess:
            data = {
                "key": '你好',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_flags_with_large_ips():
    '''Test that users with high octect IP addresses can submit flags'''
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)

        # SQLite doesn't support BigInteger well so we can't test it properly
        ip_addresses = ['172.18.0.1', '255.255.255.255', '2001:0db8:85a3:0000:0000:8a2e:0370:7334']
        for ip_address in ip_addresses:
            # Monkeypatch get_ip
            utils.get_ip = lambda: ip_address

            # Generate challenge and flag
            chal = gen_challenge(app.db)
            chal_id = chal.id
            flag = gen_flag(app.db, chal=chal.id, flag=u'correct_key')

            # Submit wrong_key
            with client.session_transaction() as sess:
                data = {
                    "key": 'wrong_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
            assert WrongKeys.query.filter_by(ip=ip_address).first()

            # Submit correct key
            with client.session_transaction() as sess:
                data = {
                    "key": 'correct_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 1 and resp.get('message') == "Correct"
            assert Solves.query.filter_by(ip=ip_address).first()
    destroy_ctfd(app)


def test_unlocking_hints_with_no_cost():
    '''Test that hints with no cost can be unlocked'''
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        assert output.get('hint') == 'This is a hint'
    destroy_ctfd(app)


def test_unlocking_hint_for_unicode_challenge():
    '''Test that hints for challenges with unicode names can be unlocked'''
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db, name=text_type('🐺'))
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        assert output.get('hint') == 'This is a hint'
    destroy_ctfd(app)


def test_that_view_challenges_unregistered_works():
    '''Test that view_challenges_unregistered works'''
    app = create_ctfd()
    with app.app_context():
        chal = gen_challenge(app.db, name=text_type('🐺'))
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)

        client = app.test_client()
        r = client.get('/chals')
        assert r.status_code == 403

        config = set_config('view_challenges_unregistered', True)

        client = app.test_client()
        r = client.get('/chals')
        data = r.get_data(as_text=True)
        assert json.loads(data)

        r = client.get('/chals/solves')
        data = r.get_data(as_text=True)
        assert json.loads(data) == {}

        r = client.get('/chal/1/solves')
        data = r.get_data(as_text=True)
        assert json.loads(data)

        with client.session_transaction() as sess:
            data = {
                "key": 'not_flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal_id), data=data)
        data = r.get_data(as_text=True)
        data = json.loads(data)
        assert data['status'] == -1
