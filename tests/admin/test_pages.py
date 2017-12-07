#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from CTFd.models import Pages
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended
from CTFd.plugins.challenges import get_chal_class
from freezegun import freeze_time
from mock import patch


def test_admin_page_create():
    """Can an admin create a page?"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages?operation=create')
        assert r.status_code == 200
        with client.session_transaction() as sess:
            data = {
                "route": "this-is-a-route",
                "html": "This is some HTML",
                "title": "Title",
                "auth_required": "on",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages?operation=publish', data=data)
        r = client.get('/admin/pages?route=this-is-a-route')
        assert r.status_code == 200

        r = client.get('/this-is-a-route')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert "This is some HTML" in output
    destroy_ctfd(app)


def test_admin_page_create_draft():
    """Draft pages should not be shown"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages?operation=create')
        assert r.status_code == 200
        with client.session_transaction() as sess:
            data = {
                "route": "this-is-a-route",
                "html": "This is some HTML",
                "title": "Title",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages?operation=save', data=data)
        r = client.get('/this-is-a-route')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_admin_page_preview():
    """Page previews should not create a new page"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "route": "this-is-a-route",
                "html": "This is some HTML",
                "title": "Title",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages?operation=preview', data=data)

        output = r.get_data(as_text=True)
        assert "This is some HTML" in output

        assert len(Pages.query.all()) == 1  # The index page counts as a page
    destroy_ctfd(app)


def test_admin_page_update():
    """Can an admin update a page?"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages?id=1')
        assert r.status_code == 200
        with client.session_transaction() as sess:
            data = {
                "route": "index",
                "html": "New Index Page",
                "title": "title",
                "id": 1,
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages?operation=save', data=data)
        r = client.get('/admin/pages?id=1')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert "New Index Page" in output

        r = client.get('/')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert "New Index Page" in output
    destroy_ctfd(app)


def test_admin_page_delete():
    """Can an admin delete a page?"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                "id": 1,
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages/delete', data=data)
        assert r.status_code == 200

        r = client.get('/')
        assert r.status_code == 404

        count = Pages.query.count()
        assert count == 0

    destroy_ctfd(app)
