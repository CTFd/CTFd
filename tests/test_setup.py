#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import get_config
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import serialize
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


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


def _submit_setup(client, theme_color):
    client.get("/setup")  # Populate session with nonce
    with client.session_transaction() as sess:
        data = {
            "ctf_name": "CTFd",
            "ctf_description": "description",
            "name": "admin",
            "email": "admin@examplectf.com",
            "password": "password",
            "user_mode": "users",
            "nonce": sess.get("nonce"),
            "ctf_theme": "core",
            "theme_color": theme_color,
        }
    return client.post("/setup", data=data)


def test_setup_theme_color_xss_rejected():
    """Test that a malicious theme_color cannot inject markup into theme_header"""
    app = create_ctfd(setup=False)
    with app.app_context():
        payload = "#fff;} </style><script>alert(document.domain)</script><style>"
        with app.test_client() as client:
            _submit_setup(client, payload)
            # The invalid color must not be stored into the rendered theme_header
            assert get_config("theme_header") is None
            r = client.get("/")
            assert r.status_code == 200
            assert "<script>alert(document.domain)</script>" not in r.get_data(
                as_text=True
            )
    destroy_ctfd(app)


def test_setup_theme_color_valid_hex_is_stored():
    """Test that a legitimate hex theme_color still populates theme_header"""
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            _submit_setup(client, "#ff0000")
            theme_header = get_config("theme_header")
            assert theme_header is not None
            assert "--theme-color: #ff0000;" in theme_header
            assert "<script>" not in theme_header
    destroy_ctfd(app)
