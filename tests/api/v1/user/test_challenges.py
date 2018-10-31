#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from tests.helpers import *
import time


def test_api_challenge_list_visibility():
    """Can the api load /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time())))  # Now
            set_config('end', str(int(time.time() + 300)))  # Five minutes from now
            set_config('challenge_visibility', 'public')
            r = client.get('/api/v1/challenges')
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges')
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_list_ctftime():
    """Can the api load /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
            set_config('end', str(int(time.time() - 60)))  # 1 minute ago
            set_config('challenge_visibility', 'public')
            r = client.get('/api/v1/challenges')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_list_user_visibility():
    """Can the user load /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        r = client.get('/api/v1/challenges')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_list_user_ctftime():
    """Can the user load /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
        set_config('end', str(int(time.time() - 60)))  # 1 minute ago
        r = client.get('/api/v1/challenges')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_list_verified_emails():
    """Can a verified email load /api/v1/challenges"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        set_config('verify_emails', True)
        r = client.get('/api/v1/challenges')
        assert r.status_code == 302
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = registered_client.get('/api/v1/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_visibility():
    """Can the api load /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time())))  # Now
            set_config('end', str(int(time.time() + 300)))  # Five minutes from now
            set_config('challenge_visibility', 'public')
            gen_challenge(app.db)
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_ctftime():
    """Can the api load /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
            set_config('end', str(int(time.time() - 60)))  # 1 minute ago
            set_config('challenge_visibility', 'public')
            gen_challenge(app.db)
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_user_visibility():
    """Can the user load /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_user_ctftime():
    """Can the user load /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
        set_config('end', str(int(time.time() - 60)))  # 1 minute ago
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_verified_emails():
    """Can a verified email load /api/v1/challenges/<challenge_id>"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        set_config('verify_emails', True)
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 302
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = registered_client.get('/api/v1/challenges/1')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id> 404"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_solves_visibility():
    """Can the api load /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time())))  # Now
            set_config('end', str(int(time.time() + 300)))  # Five minutes from now
            set_config('challenge_visibility', 'public')
            gen_challenge(app.db)
            r = client.get('/api/v1/challenges/1/solves')
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges/1/solves')
            assert r.status_code == 302
    destroy_ctfd(app)


def test_api_challenge_solves_ctftime():
    """Can the api load /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a non-logged in client and ensure challenges are available
        with app.test_client() as client:
            set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
            set_config('end', str(int(time.time() - 60)))  # 1 minute ago
            set_config('challenge_visibility', 'public')
            gen_challenge(app.db)
            r = client.get('/api/v1/challenges/1/solves')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_solves_user_visibility():
    """Can the user load /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_solves_user_ctftime():
    """Can the user load /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time() - 300)))  # 5 minutes ago
        set_config('end', str(int(time.time() - 60)))  # 1 minute ago
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_solves_verified_emails():
    """Can a verified email load /api/v1/challenges/<challenge_id>/solves"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        set_config('verify_emails', True)
        gen_challenge(app.db)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 302
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = registered_client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_solves_score_visibility():
    """Can a user load /api/v1/challenges/<challenge_id>/solves if score_visibility is public/private/admin"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        set_config('challenge_visibility', 'public')
        set_config('score_visibility', 'public')
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/solves')
            print("STATUS", r.status_code)
            assert r.status_code == 200
        # Create a logged in client and ensure challenges are available
        set_config('challenge_visibility', 'private')
        set_config('score_visibility', 'private')
        register_user(app)
        private_client = login_as_user(app)
        r = private_client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
        set_config('score_visibility', 'admin')
        admin = login_as_user(app, 'admin', 'password')
        r = admin.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_solves_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id>/solves 404"""
    app = create_ctfd()
    with app.app_context():
        # Create a logged in client and ensure challenges are available
        register_user(app)
        client = login_as_user(app)
        set_config('start', str(int(time.time())))  # Now
        set_config('end', str(int(time.time() + 300)))  # 5 minutes from now
        r = client.get('/api/v1/challenges/1/solves')
        print("STATUS", r.status_code)
        assert r.status_code == 404
    destroy_ctfd(app)
