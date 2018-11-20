#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_ctfd_setup_redirect():
    """Test that a fresh CTFd instance redirects to /setup"""
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/users')
            assert r.status_code == 302
            assert r.location == "http://localhost/setup"

            # Files in /themes load properly
            r = client.get('/themes/core/static/css/style.css')
            assert r.status_code == 200
    destroy_ctfd(app)
