#!/usr/bin/env python
# -*- coding: utf-8 -*-

from freezegun import freeze_time
from tests.helpers import *


def test_user_get_scoreboard():
    """Can a registered user load /scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scores():
    """Can a registered user load /api/v1/scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_topteams():
    """Can a registered user load /api/v1/scoreboard/top/10"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/scoreboard/top/10')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_score_is_correct():
    """Test that a user's score is correct"""
    app = create_ctfd()
    with app.app_context():
        # create user1
        register_user(app, name="user1", email="user1@ctfd.io")

        # create challenge
        chal = gen_challenge(app.db, value=100)
        flag = gen_flag(app.db, challenge_id=chal.id, content='flag')
        chal_id = chal.id

        # create a solve for the challenge for user1. (the id is 2 because of the admin)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)
        user1 = Users.query.filter_by(id=2).first()

        # assert that user1's score is 100
        assert user1.score == 100
        assert user1.place == '1st'

        # create user2
        register_user(app, name="user2", email="user2@ctfd.io")

        # user2 solves the challenge
        gen_solve(app.db, 3, challenge_id=chal_id)

        # assert that user2's score is 100 but is in 2nd place
        user2 = Users.query.filter_by(id=3).first()
        assert user2.score == 100
        assert user2.place == '2nd'

        # create an award for user2
        gen_award(app.db, user_id=3, value=5)

        # assert that user2's score is now 105 and is in 1st place
        assert user2.score == 105
        assert user2.place == '1st'
    destroy_ctfd(app)


def test_top_10():
    """Make sure top10 returns correct information"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io")
        register_user(app, name="user2", email="user2@ctfd.io")
        register_user(app)

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, challenge_id=chal1.id, content='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, challenge_id=chal2.id, content='flag')
        chal2_id = chal2.id

        # Generates solve for user1
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, user_id=2, challenge_id=chal1_id)

        with freeze_time("2017-10-4 03:25:45"):
            gen_solve(app.db, user_id=2, challenge_id=chal2_id)

        # Generate solve for user2
        with freeze_time("2017-10-3 03:21:34"):
            gen_solve(app.db, user_id=3, challenge_id=chal1_id)

        client = login_as_user(app)
        r = client.get('/api/v1/scoreboard/top/10')
        response = r.get_json()['data']

        saved = {
            '1': {
                'id': 2,
                'solves': [{
                    'date': '2017-10-03T03:21:34Z',
                    'challenge_id': 1,
                    'account_id': 2,
                    'user_id': 2,
                    'team_id': None,
                    'value': 100
                }, {
                    'date': '2017-10-04T03:25:45Z',
                    'challenge_id': 2,
                    'account_id': 2,
                    'user_id': 2,
                    'team_id': None,
                    'value': 100
                }],
                'name': 'user1'
            }, '2': {
                'id': 3,
                'solves': [{
                    'date': '2017-10-03T03:21:34Z',
                    'challenge_id': 1,
                    'account_id': 3,
                    'user_id': 3,
                    'team_id': None,
                    'value': 100
                }],
                'name': 'user2'
            }
        }
        assert saved == response
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
        flag1 = gen_flag(app.db, challenge_id=chal1.id, content='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, challenge_id=chal2.id, content='flag')
        chal2_id = chal2.id

        # user1 solves chal1
        with freeze_time("2017-10-3 03:21:34"):
            with client1.session_transaction() as sess:
                data = {
                    "submission": 'flag',
                    "challenge_id": chal1_id
                }
                r = client1.post('/api/v1/challenges/attempt', json=data)

        # user1 is now on top
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user1'

        # user2 solves chal1 and chal2
        with freeze_time("2017-10-4 03:30:34"):
            with client2.session_transaction() as sess:
                # solve chal1
                data = {
                    "submission": 'flag',
                    "challenge_id": chal1_id
                }
                r = client2.post('/api/v1/challenges/attempt', json=data)
                # solve chal2
                data = {
                    "submission": 'flag',
                    "challenge_id": chal2_id
                }
                r = client2.post('/api/v1/challenges/attempt', json=data)

        # user2 is now on top
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user2'

        # user1 solves chal2
        with freeze_time("2017-10-5 03:50:34"):
            with client1.session_transaction() as sess:
                data = {
                    "submission": 'flag',
                    "challenge_id": chal2_id
                }
                r = client1.post('/api/v1/challenges/attempt', json=data)

        # user2 should still be on top because they solved chal2 first
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user2'
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
        flag1 = gen_flag(app.db, challenge_id=chal1.id, content='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, challenge_id=chal2.id, content='flag')
        chal2_id = chal2.id

        # A 0 point challenge shouldn't influence the scoreboard (see #577)
        chal0 = gen_challenge(app.db, value=0)
        flag0 = gen_flag(app.db, challenge_id=chal0.id, content='flag')
        chal0_id = chal0.id

        # user1 solves chal1
        with freeze_time("2017-10-3 03:21:34"):
            with client1.session_transaction() as sess:
                data = {
                    "submission": 'flag',
                    "challenge_id": chal1_id
                }
                r = client1.post('/api/v1/challenges/attempt', json=data)

        # user1 is now on top
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user1'

        # user2 solves chal1 and chal2
        with freeze_time("2017-10-4 03:30:34"):
            with client2.session_transaction() as sess:
                # solve chal1
                data = {
                    "submission": 'flag',
                    "challenge_id": chal1_id
                }
                r = client2.post('/api/v1/challenges/attempt'.format(chal1_id), json=data)
                # solve chal2
                data = {
                    "submission": 'flag',
                    "challenge_id": chal2_id
                }
                r = client2.post('/api/v1/challenges/attempt'.format(chal2_id), json=data)

        # user2 is now on top
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user2'

        # user1 solves chal2
        with freeze_time("2017-10-5 03:50:34"):
            with client1.session_transaction() as sess:
                data = {
                    "submission": 'flag',
                    "challenge_id": chal2_id
                }
                r = client1.post('/api/v1/challenges/attempt'.format(chal2_id), json=data)

        # user2 should still be on top because they solved chal2 first
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user2'

        # user2 solves a 0 point challenge
        with freeze_time("2017-10-5 03:55:34"):
            with client2.session_transaction() as sess:
                data = {
                    "submission": 'flag',
                    "challenge_id": chal0_id
                }
                r = client2.post('/api/v1/challenges/attempt'.format(chal0_id), json=data)

        # user2 should still be on top because 0 point challenges should not tie break
        scores = get_scores(admin)
        assert scores[0]['name'] == 'user2'
    destroy_ctfd(app)
