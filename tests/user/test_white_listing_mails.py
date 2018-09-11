#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


# Any user can register if there is allowed domain and allowed mail is undefined is the default registration. No need for new test.


def test_user_can_register_allowed_mail_domain():
    """User can register a mail from a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        allowed_domains = ['ctfd.io']
        set_config('allowed_domains', json.dumps(allowed_domains))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_user_cannot_register_disallowed_mail_domain():
    """User cannot register a mail that is not in a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        allowed_domains = ['ctfd.io']
        set_config('allowed_domains', json.dumps(allowed_domains))
        register_user(app, name="user1", email="user1@ctfd2.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 1  # There's only the admin user
    destroy_ctfd(app)


def test_user_can_register_allowed_mail():
    """User can register a white-listed mail"""
    app = create_ctfd()
    with app.app_context():
        allowed_mails = ['user1@ctfd.io']
        set_config('allowed_mails', json.dumps(allowed_mails))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_user_cannot_register_disallowed_mail():
    """User cannot register a mail that is not white-listed"""
    app = create_ctfd()
    with app.app_context():
        allowed_mails = ['user1@ctfd.io']
        set_config('allowed_mails', json.dumps(allowed_mails))
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 1  # There's only the admin user
    destroy_ctfd(app)


def test_user_can_change_to_allowed_mail_domain():
    """User can change to a mail from a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        allowed_domains = ['ctfd.io', 'ctfd2.io']
        set_config('allowed_domains', json.dumps(allowed_domains))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client = login_as_user(app, name="user1", password="password")
        r = client.get('/profile')
        with client.session_transaction() as sess:
            data = {
                'name': 'user1',
                'email': 'user1@ctfd2.io',
                'confirm': '',
                'password': '',
                'affiliation': 'affiliation_test',
                'website': 'https://ctfd.io',
                'country': 'United States of America',
                'nonce': sess.get('nonce')
            }

        r = client.post('/profile', data=data)

        user = Teams.query.filter_by(name='user1').first()
        assert user.email == 'user1@ctfd2.io'
        assert user.affiliation == 'affiliation_test'
        assert user.website == 'https://ctfd.io'
        assert user.country == 'United States of America'
    destroy_ctfd(app)


def test_user_cannot_change_to_disallowed_mail_domain():
    """User cannot change to a mail that is not in a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        allowed_domains = ['ctfd.io', 'ctfd2.io']
        set_config('allowed_domains', json.dumps(allowed_domains))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client = login_as_user(app, name="user1", password="password")
        r = client.get('/profile')
        with client.session_transaction() as sess:
            data = {
                'name': 'user1',
                'email': 'user1@ctfd3.io',
                'confirm': '',
                'password': '',
                'affiliation': 'affiliation_test',
                'website': 'https://ctfd.io',
                'country': 'United States of America',
                'nonce': sess.get('nonce')
            }

        r = client.post('/profile', data=data)

        user = Teams.query.filter_by(name='user1').first()
        assert user.email == 'user1@ctfd.io'
        assert user.affiliation is None
        assert user.website is None
        assert user.country is None
    destroy_ctfd(app)


def test_user_can_change_to_allowed_mail():
    """User can change to a mail that is white-listed"""
    app = create_ctfd()
    with app.app_context():
        allowed_mails = ['user1@ctfd.io', 'user1@ctfd2.io']
        set_config('allowed_mails', json.dumps(allowed_mails))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client = login_as_user(app, name="user1", password="password")
        r = client.get('/profile')
        with client.session_transaction() as sess:
            data = {
                'name': 'user1',
                'email': 'user1@ctfd2.io',
                'confirm': '',
                'password': '',
                'affiliation': 'affiliation_test',
                'website': 'https://ctfd.io',
                'country': 'United States of America',
                'nonce': sess.get('nonce')
            }

        r = client.post('/profile', data=data)

        user = Teams.query.filter_by(name='user1').first()
        assert user.email == 'user1@ctfd2.io'
        assert user.affiliation == 'affiliation_test'
        assert user.website == 'https://ctfd.io'
        assert user.country == 'United States of America'
    destroy_ctfd(app)


def test_user_cannot_change_to_disallowed_mail():
    """User cannot change to a mail that is not white-listed"""
    app = create_ctfd()
    with app.app_context():
        allowed_mails = ['user1@ctfd.io', 'user1@ctfd2.io']
        set_config('allowed_mails', json.dumps(allowed_mails))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client = login_as_user(app, name="user1", password="password")
        r = client.get('/profile')
        with client.session_transaction() as sess:
            data = {
                'name': 'user1',
                'email': 'user2@ctfd.io',
                'confirm': '',
                'password': '',
                'affiliation': 'affiliation_test',
                'website': 'https://ctfd.io',
                'country': 'United States of America',
                'nonce': sess.get('nonce')
            }

        r = client.post('/profile', data=data)

        user = Teams.query.filter_by(name='user1').first()
        assert user.email == 'user1@ctfd.io'
        assert user.affiliation is None
        assert user.website is None
        assert user.country is None
    destroy_ctfd(app)
