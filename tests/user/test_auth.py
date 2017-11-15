#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_user_can_view_challenges():
    """Test that user_can_view_challenges allows users to view challenges while not logged in"""
    app = create_ctfd()
    with app.app_context():
        set_config('view_challenges_unregistered', True)
        utils.cache.clear()  # Need to clear the cached configuration
        chal = gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 200
            r = client.get('/chals')
            assert r.status_code == 200
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('view_challenges_unregistered', False)
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 302
            r = client.get('/chals')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_verify_emails_config():
    """Test that users can only solve challenges if they are logged in and verified if verify_emails is set"""
    app = create_ctfd()
    with app.app_context():
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('verify_emails', True)
        chal = gen_challenge(app.db)

        register_user(app)
        client = login_as_user(app)

        r = client.get('/challenges')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        r = client.get('/chals')
        assert r.status_code == 403

        user = Teams.query.filter_by(id=2).first()
        user.verified = True
        app.db.session.commit()

        r = client.get('/challenges')
        assert r.status_code == 200

        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_verify_and_view_unregistered():
    """If both verify_emails and user_can_view_challenges are set, the user should see challenges while unregistered
    but be locked out if they register until they confirm their email address"""
    app = create_ctfd()
    with app.app_context():
        utils.cache.clear()  # Need to clear the cached configuration
        set_config('view_challenges_unregistered', True)
        set_config('verify_emails', True)
        chal = gen_challenge(app.db)

        # We are not authed but we should still be able to see challenges
        with app.test_client() as client:
            r = client.get('/challenges')
            assert r.status_code == 200

            r = client.get('/chals')
            assert r.status_code == 200

        # Logging in...
        register_user(app)
        client = login_as_user(app)

        # We are now logged in so we should be redirected to the confirmation page
        r = client.get('/challenges')
        assert r.location == "http://localhost/confirm"
        assert r.status_code == 302

        r = client.get('/chals')
        assert r.status_code == 403

        user = Teams.query.filter_by(id=2).first()
        user.verified = True
        app.db.session.commit()

        # Double check that we can see challenges
        r = client.get('/challenges')
        assert r.status_code == 200

        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)
