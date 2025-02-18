#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.exceptions import SecurityError

from CTFd.config import TestingConfig
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_reverse_proxy_config():
    """Test that REVERSE_PROXY configuration behaves properly"""

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = "1,2,3,4"

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 2
        assert app.wsgi_app.x_host == 3
        assert app.wsgi_app.x_port == 4
        assert app.wsgi_app.x_prefix == 0
    destroy_ctfd(app)

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = "true"

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 1
        assert app.wsgi_app.x_host == 1
        assert app.wsgi_app.x_port == 1
        assert app.wsgi_app.x_prefix == 1
    destroy_ctfd(app)

    class ReverseProxyConfig(TestingConfig):
        REVERSE_PROXY = True

    app = create_ctfd(config=ReverseProxyConfig)
    with app.app_context():
        assert app.wsgi_app.x_for == 1
        assert app.wsgi_app.x_proto == 1
        assert app.wsgi_app.x_host == 1
        assert app.wsgi_app.x_port == 1
        assert app.wsgi_app.x_prefix == 1
    destroy_ctfd(app)


def test_server_sent_events_config():
    """Test that SERVER_SENT_EVENTS configuration behaves properly"""

    class ServerSentEventsConfig(TestingConfig):
        SERVER_SENT_EVENTS = False

    app = create_ctfd(config=ServerSentEventsConfig)
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/events")
        assert r.status_code == 204
    destroy_ctfd(app)


def test_trusted_hosts_config():
    """Test that TRUSTED_HOSTS configuration behaves properly"""

    class TrustedHostsConfig(TestingConfig):
        SERVER_NAME = "example.com"
        TRUSTED_HOSTS = ["example.com"]

    app = create_ctfd(config=TrustedHostsConfig)
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get("/", headers={"Host": "example.com"})
        assert r.status_code == 200

        # TODO: We need to allow either a 500 or a 400 because Flask-RestX
        # seems to be overriding Flask's error handler
        try:
            r = client.get("/", headers={"Host": "evil.com"})
        except SecurityError:
            pass
        else:
            if r.status_code != 400:
                raise SecurityError("Responded to untrusted request")
    destroy_ctfd(app)
