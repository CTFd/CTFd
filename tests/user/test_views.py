#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_themes_handler():
    """Test that the themes handler is working properly"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/themes/core/static/css/style.css')
            assert r.status_code == 200
            r = client.get('/themes/core/static/css/404_NOT_FOUND')
            assert r.status_code == 404
            r = client.get('/themes/core/static/%2e%2e/%2e%2e/%2e%2e/utils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/%2e%2e%2f%2e%2e%2f%2e%2e%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/..%2f..%2f..%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/core/static/../../../utils.py')
            assert r.status_code == 404
    destroy_ctfd(app)