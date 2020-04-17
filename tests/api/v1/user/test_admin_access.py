#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_api_hint_404():
    """Are admin protected resources accessible by admins/non-admins"""
    app = create_ctfd()
    endpoints = [
        "/api/v1/configs/{}",
        "/api/v1/challenges/types",
        "/api/v1/statistics/teams",
        "/api/v1/flags/{}",
        "/api/v1/statistics/users/{}",
        "/api/v1/configs",
        "/api/v1/statistics/challenges/solves/percentages",
        "/api/v1/statistics/scores/distribution",
        "/api/v1/tags/{}",
        "/api/v1/pages",
        "/api/v1/files/{}",
        "/api/v1/challenges/{}/tags",
        "/api/v1/hints",
        "/api/v1/challenges/{}/files",
        "/api/v1/flags",
        "/api/v1/submissions/{}",
        "/api/v1/challenges/{}/flags",
        "/api/v1/awards/{}",
        "/api/v1/unlocks",
        "/api/v1/challenges/{}/hints",
        "/api/v1/statistics/submissions/{}",
        "/api/v1/flags/types/{}",
        "/api/v1/tags",
        "/api/v1/statistics/challenges/{}",
        "/api/v1/files",
        "/api/v1/flags/types",
        "/api/v1/submissions",
        "/api/v1/pages/{}",
    ]

    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        for endpoint in endpoints:
            r = client.get(endpoint.format(1))
            assert r.status_code == 302
            assert r.location.startswith("http://localhost/login")
    destroy_ctfd(app)
