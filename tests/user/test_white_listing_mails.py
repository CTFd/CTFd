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


def test_user_can_register_mail_from_whitelisted_domain():
    """User can register a mail from a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        white_listed_domains = ['ctfd.io']
        set_config('white_listed_domains', json.dumps(white_listed_domains))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_user_cannot_register_mail_not_in_whitelisted_domain():
    """User cannot register a mail that is not in a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        white_listed_domains = ['ctfd.io']
        set_config('white_listed_domains', json.dumps(white_listed_domains))
        register_user(app, name="user1", email="user1@ctfd2.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 1  # There's only the admin user
    destroy_ctfd(app)


def test_user_can_register_mail_from_whitelisted_addresses():
    """User can register a white-listed mail"""
    app = create_ctfd()
    with app.app_context():
        white_listed_addresses = ['user1@ctfd.io']
        set_config('white_listed_addresses', json.dumps(white_listed_addresses))
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_user_cannot_register_mail_not_in_whitelisted_addresses():
    """User cannot register a mail that is not white-listed"""
    app = create_ctfd()
    with app.app_context():
        white_listed_addresses = ['user1@ctfd.io']
        set_config('white_listed_addresses', json.dumps(white_listed_addresses))
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 1  # There's only the admin user
    destroy_ctfd(app)


def test_user_can_change_mail_to_whitelisted_domain():
    """User can change to a mail in a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        white_listed_domains = ['ctfd.io', 'ctfd2.io']
        set_config('white_listed_domains', json.dumps(white_listed_domains))
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
    destroy_ctfd(app)


def test_user_cannot_change_mail_not_in_whitelisted_domain():
    """User cannot change to a mail that is not in a white-listed domain"""
    app = create_ctfd()
    with app.app_context():
        white_listed_domains = ['ctfd.io', 'ctfd2.io']
        set_config('white_listed_domains', json.dumps(white_listed_domains))
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
    destroy_ctfd(app)


def test_user_can_change_mail_to_whitelisted_addresses():
    """User can change to a mail that is white-listed"""
    app = create_ctfd()
    with app.app_context():
        white_listed_addresses = ['user1@ctfd.io', 'user1@ctfd2.io']
        set_config('white_listed_addresses', json.dumps(white_listed_addresses))
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
    destroy_ctfd(app)


def test_user_cannot_change_mail_not_in_whitelisted_addresses():
    """User cannot change to a mail that is not white-listed"""
    app = create_ctfd()
    with app.app_context():
        white_listed_addresses = ['user1@ctfd.io', 'user1@ctfd2.io']
        set_config('white_listed_addresses', json.dumps(white_listed_addresses))
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
    destroy_ctfd(app)
