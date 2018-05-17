#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_top_10():
    '''Make sure top10 returns correct information'''
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io")
        register_user(app, name="user2", email="user2@ctfd.io")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, chal=chal2.id, flag='flag')
        chal2_id = chal2.id

        # Generates solve for user1
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, teamid=2, chalid=chal1_id)

        with freeze_time("2017-10-4 03:25:45"):
            gen_solve(app.db, teamid=2, chalid=chal2_id)

        # Generate solve for user2
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, teamid=3, chalid=chal1_id)

        client = login_as_user(app)
        r = client.get('/top/10')
        response = r.get_data(as_text=True)

        saved = '''{
          "places": {
            "1": {
              "id": 2,
              "name": "user1",
              "solves": [
                {
                  "chal": 1,
                  "team": 2,
                  "time": 1507000894,
                  "value": 100
                },
                {
                  "chal": 2,
                  "team": 2,
                  "time": 1507087545,
                  "value": 100
                }
              ]
            },
            "2": {
              "id": 3,
              "name": "user2",
              "solves": [
                {
                  "chal": 1,
                  "team": 3,
                  "time": 1507000894,
                  "value": 100
                }
              ]
            }
          }
        }'''
        saved = json.loads(saved)
        received = json.loads(response)
        assert saved == received
    destroy_ctfd(app)


def test_scoring_logic():
    """Test that scoring logic is correct"""
    app = create_ctfd()
    with app.app_context():
        admin = login_as_user(app, name="admin", password="password")

        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client1 = login_as_user(app, name="user1", password="password")
        register_user(app, name="user2", email="user2@ctfd.io", password="password")
        client2 = login_as_user(app, name="user2", password="password")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, chal=chal2.id, flag='flag')
        chal2_id = chal2.id

        # user1 solves chal1
        with freeze_time("2017-10-3 03:21:34"):
            with client1.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client1.post('/chal/{}'.format(chal1_id), data=data)

        # user1 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user1'

        # user2 solves chal1 and chal2
        with freeze_time("2017-10-4 03:30:34"):
            with client2.session_transaction() as sess:
                # solve chal1
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client2.post('/chal/{}'.format(chal1_id), data=data)
                # solve chal2
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client2.post('/chal/{}'.format(chal2_id), data=data)

        # user2 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'

        # user1 solves chal2
        with freeze_time("2017-10-5 03:50:34"):
            with client1.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client1.post('/chal/{}'.format(chal2_id), data=data)

        # user2 should still be on top because they solved chal2 first
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'
    destroy_ctfd(app)


def test_scoring_logic_with_zero_point_challenges():
    """Test that scoring logic is correct with zero point challenges. Zero point challenges should not tie break"""
    app = create_ctfd()
    with app.app_context():
        admin = login_as_user(app, name="admin", password="password")

        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client1 = login_as_user(app, name="user1", password="password")
        register_user(app, name="user2", email="user2@ctfd.io", password="password")
        client2 = login_as_user(app, name="user2", password="password")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, chal=chal2.id, flag='flag')
        chal2_id = chal2.id

        # A 0 point challenge shouldn't influence the scoreboard (see #577)
        chal0 = gen_challenge(app.db, value=0)
        flag0 = gen_flag(app.db, chal=chal0.id, flag='flag')
        chal0_id = chal0.id

        # user1 solves chal1
        with freeze_time("2017-10-3 03:21:34"):
            with client1.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client1.post('/chal/{}'.format(chal1_id), data=data)

        # user1 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user1'

        # user2 solves chal1 and chal2
        with freeze_time("2017-10-4 03:30:34"):
            with client2.session_transaction() as sess:
                # solve chal1
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client2.post('/chal/{}'.format(chal1_id), data=data)
                # solve chal2
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client2.post('/chal/{}'.format(chal2_id), data=data)

        # user2 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'

        # user1 solves chal2
        with freeze_time("2017-10-5 03:50:34"):
            with client1.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client1.post('/chal/{}'.format(chal2_id), data=data)

        # user2 should still be on top because they solved chal2 first
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'

        # user2 solves a 0 point challenge
        with freeze_time("2017-10-5 03:55:34"):
            with client2.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
                r = client2.post('/chal/{}'.format(chal0_id), data=data)

        # user2 should still be on top because 0 point challenges should not tie break
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'
    destroy_ctfd(app)
