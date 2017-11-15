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
        r = client.get('/admin/pages?mode=create')
        assert r.status_code == 200
        with client.session_transaction() as sess:
            data = {
                "route": "this-is-a-route",
                "html": "This is some HTML",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages', data=data)
        r = client.get('/admin/pages?route=this-is-a-route')
        assert r.status_code == 200

        r = client.get('/this-is-a-route')
        assert r.status_code == 200
        output = r.get_data(as_text=True)
        assert "This is some HTML" in output
    destroy_ctfd(app)


def test_admin_page_update():
    """Can an admin update a page?"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages?route=index')
        assert r.status_code == 200
        with client.session_transaction() as sess:
            data = {
                "route": "index",
                "html": "New Index Page",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages', data=data)
        r = client.get('/admin/pages?route=index')
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
                "route": "index",
                "nonce": sess.get('nonce')
            }
        r = client.post('/admin/pages/delete', data=data)
        assert r.status_code == 200

        r = client.get('/')
        assert r.status_code == 404

        count = Pages.query.count()
        assert count == 0

    destroy_ctfd(app)
