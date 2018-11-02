#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
