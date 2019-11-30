#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    register_user,
    login_as_user,
)
from CTFd.utils import get_config
from CTFd.utils.security.signing import serialize
from CTFd.utils.security.csrf import generate_nonce


def test_setup_integrations():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = login_as_user(app)
        r = user.get("/setup/integrations")
        assert r.status_code == 403

        admin = login_as_user(app, "admin")
        r = admin.get("/setup/integrations")
        assert r.status_code == 403

        admin = login_as_user(app, "admin")

        url = "/setup/integrations?state={state}&mlc_client_id=client_id&mlc_client_secret=client_secret&name=mlc".format(
            state=serialize(generate_nonce())
        )
        r = admin.get(url)
        assert r.status_code == 200
        assert get_config("oauth_client_id") == "client_id"
        assert get_config("oauth_client_secret") == "client_secret"
    destroy_ctfd(app)
