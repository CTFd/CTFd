#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys, Challenges
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


def test_viewing_challenge():
    """Test that users can see individual challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get('/chals/1')
        assert json.loads(r.get_data(as_text=True))
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
        for c in range(6):
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
              "5": 1,
              "6": 0
            }
            ''')
            received = json.loads(output)
            assert saved == received
        set_config('hide_scores', True)
        with client.session_transaction() as sess:
            r = client.get('/chals/solves')
            output = r.get_data(as_text=True)
            saved = json.loads('''{
              "1": -1,
              "2": -1,
              "3": -1,
              "4": -1,
              "5": -1,
              "6": -1
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


def test_submitting_correct_static_case_insensitive_flag():
    """Test that correct static flags are correct if the static flag is marked case_insensitive"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag', data="case_insensitive")
        with client.session_transaction() as sess:
            data = {
                "key": 'FLAG',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_correct_regex_case_insensitive_flag():
    """Test that correct regex flags are correct if the regex flag is marked case_insensitive"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, key_type='regex', flag='flag', data="case_insensitive")
        with client.session_transaction() as sess:
            data = {
                "key": 'FLAG',
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


def test_challenges_with_max_attempts():
    """Test that users are locked out of a challenge after they reach max_attempts"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal = Challenges.query.filter_by(id=chal.id).first()
        chal_id = chal.id
        chal.max_attempts = 3
        app.db.session.commit()

        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')
        for x in range(3):
            with client.session_transaction() as sess:
                data = {
                    "key": 'notflag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)

        wrong_keys = WrongKeys.query.all()
        assert len(wrong_keys) == 3

        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal_id), data=data)
        assert r.status_code == 200

        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 0 and resp.get('message') == "You have 0 tries remaining"

        solves = Solves.query.all()
        assert len(solves) == 0
    destroy_ctfd(app)


def test_challenge_kpm_limit():
    """Test that users are properly ratelimited when submitting flags"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id

        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')
        for x in range(11):
            with client.session_transaction() as sess:
                data = {
                    "key": 'notflag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)

        wrong_keys = WrongKeys.query.all()
        assert len(wrong_keys) == 11

        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal_id), data=data)
        assert r.status_code == 200

        wrong_keys = WrongKeys.query.all()
        assert len(wrong_keys) == 12

        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 3 and resp.get('message') == "You're submitting keys too fast. Slow down."

        solves = Solves.query.all()
        assert len(solves) == 0
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
            def get_ip_fake(req=None):
                return ip_address
            utils.get_ip = get_ip_fake

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
    """Test that hints with no cost can be unlocked"""
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


def test_unlocking_hints_with_cost_during_ctf_with_points():
    """Test that hints with a cost are unlocked if you have the points"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id, cost=10)
        gen_award(app.db, teamid=2)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        assert output.get('hint') == 'This is a hint'
        user = Teams.query.filter_by(id=2).first()
        assert user.score() == 90
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_ctf_without_points():
    """Test that hints with a cost are not unlocked if you don't have the points"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id, cost=10)

        client = login_as_user(app)
        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
        r = client.post('/hints/1', data=data)
        output = r.get_data(as_text=True)
        output = json.loads(output)
        assert output.get('errors') == 'Not enough points'
        user = Teams.query.filter_by(id=2).first()
        assert user.score() == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_before_ctf():
    """Test that hints without a cost are not unlocked if the CTF hasn't begun"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id)
        gen_award(app.db, teamid=2)

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-1"):
            client = login_as_user(app)
            with client.session_transaction() as sess:
                data = {
                    "nonce": sess.get('nonce')
                }
            r = client.post('/hints/1', data=data)
            assert r.status_code == 403
            user = Teams.query.filter_by(id=2).first()
            assert user.score() == 100
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_ended_ctf():
    """Test that hints with a cost are not unlocked if the CTF has ended"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        hint = gen_hint(app.db, chal_id, cost=10)
        gen_award(app.db, teamid=2)

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-11-4"):
            client = login_as_user(app)
            with client.session_transaction() as sess:
                data = {
                    "nonce": sess.get('nonce')
                }
            r = client.post('/hints/1', data=data)
            assert r.status_code == 403
            user = Teams.query.filter_by(id=2).first()
            assert user.score() == 100
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_unlocking_hints_with_cost_during_frozen_ctf():
    """Test that hints with a cost are unlocked if the CTF is frozen."""
    app = create_ctfd()
    with app.app_context():
        set_config('freeze', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        with freeze_time("2017-10-4"):
            register_user(app)
            chal = gen_challenge(app.db)
            chal_id = chal.id
            hint = gen_hint(app.db, chal_id, cost=10)
            gen_award(app.db, teamid=2)

        with freeze_time("2017-10-8"):
            client = login_as_user(app)
            with client.session_transaction() as sess:
                data = {
                    "nonce": sess.get('nonce')
                }

            r = client.post('/hints/1', data=data)
            output = r.get_data(as_text=True)
            output = json.loads(output)
            assert output.get('hint') == 'This is a hint'
            user = Teams.query.filter_by(id=2).first()
            assert user.score() == 100
    destroy_ctfd(app)


def test_unlocking_hint_for_unicode_challenge():
    """Test that hints for challenges with unicode names can be unlocked"""
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
        assert json.loads(data) == json.loads('''{
              "1": 0
            }
            ''')

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
    destroy_ctfd(app)


def test_hidden_challenge_is_unsolveable():
    """Test that hidden challenges return 404 and do not insert a solve or wrong key"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db, hidden=True)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 404

        solves = Solves.query.all()
        assert len(solves) == 0

        wrong_keys = WrongKeys.query.all()
        assert len(wrong_keys) == 0
    destroy_ctfd(app)


def test_challenges_cannot_be_solved_while_paused():
    """Test that challenges cannot be solved when the CTF is paused"""
    app = create_ctfd()
    with app.app_context():
        set_config('paused', True)

        register_user(app)
        client = login_as_user(app)

        r = client.get('/challenges')
        assert r.status_code == 200

        # Assert that there is a paused message
        data = r.get_data(as_text=True)
        assert 'paused' in data

        chal = gen_challenge(app.db, hidden=True)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)

        # Assert that the JSON message is correct
        data = r.get_data(as_text=True)
        data = json.loads(data)
        assert data['status'] == 3
        assert data['message'] == 'CTFd is paused'

        # There are no solves saved
        solves = Solves.query.all()
        assert len(solves) == 0

        # There are no wrong keys saved
        wrong_keys = WrongKeys.query.all()
        assert len(wrong_keys) == 0
    destroy_ctfd(app)


def test_challenge_solves_can_be_seen():
    """Test that the /solves endpoint works properly for users"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        with app.test_client() as client:
            r = client.get('/solves')
            assert r.location.startswith("http://localhost/login?next=")
            assert r.status_code == 302

        client = login_as_user(app)

        r = client.get('/solves')
        data = r.get_data(as_text=True)
        data = json.loads(data)

        assert len(data['solves']) == 0

        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal_id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal_id), data=data)

        data = r.get_data(as_text=True)
        data = json.loads(data)

        r = client.get('/solves')
        data = r.get_data(as_text=True)
        data = json.loads(data)

        assert len(data['solves']) > 0

        team = Teams.query.filter_by(id=2).first()
        team.banned = True
        db.session.commit()

        r = client.get('/solves')
        data = r.get_data(as_text=True)
        data = json.loads(data)

        team = Teams.query.filter_by(id=2).first()
        assert team.banned
        assert len(data['solves']) > 0
    destroy_ctfd(app)
