#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Unlocks
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_hint,
    login_as_user,
    register_user,
)


def test_api_unlock_ignores_forged_ip():
    """Test that a user cannot forge the IP address stored in an Unlock"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_hint(app.db, challenge_id=1, cost=0)
        register_user(app)

        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/unlocks",
                json={"target": 1, "type": "hints", "ip": "198.51.100.99"},
                environ_base={"REMOTE_ADDR": "203.0.113.10"},
            )
            assert r.status_code == 200

            unlock = Unlocks.query.first()
            assert unlock.ip == "203.0.113.10"
            assert r.get_json()["data"]["ip"] == "203.0.113.10"
    destroy_ctfd(app)
