#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from tests.helpers import *
from freezegun import freeze_time


def test_api_hint_404():
    """Can the users load /api/v1/hints/<hint_id> if logged in/out"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/hints/1')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_hint_visibility():
    """Can the users load /api/v1/hints/<hint_id> if logged in/out"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id)
        with app.test_client() as non_logged_in_user:
            r = non_logged_in_user.get('/api/v1/hints/1')
            assert r.status_code == 302
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/hints/1')
        assert r.status_code == 200
    destroy_ctfd(app)
