#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.plugins.challenges import CHALLENGE_CLASSES, CTFdStandardChallenge
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    register_user,
)


def test_challenge_read_output_reaches_rendered_view():
    """Test that a custom challenge type's read() output is used when rendering the challenge view"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        admin_client = login_as_user(app, name="admin", password="password")

        class ReadOverrideChallenge(CTFdStandardChallenge):
            id = "read_override"
            name = "read_override"

            @classmethod
            def read(cls, challenge):
                data = super().read(challenge)
                data["connection_info"] = "nc overridden.connection 1337"
                return data

        CHALLENGE_CLASSES["read_override"] = ReadOverrideChallenge
        try:
            challenge_data = {
                "name": "read_override",
                "category": "category",
                "description": "read override description",
                "value": 100,
                "state": "visible",
                "type": "read_override",
            }
            r = admin_client.post("/api/v1/challenges", json=challenge_data)
            assert r.status_code == 200
            challenge_id = r.get_json()["data"]["id"]

            # The API response should contain the read() override...
            user_client = login_as_user(app)
            r = user_client.get(f"/api/v1/challenges/{challenge_id}")
            assert r.status_code == 200
            data = r.get_json()["data"]
            assert data["connection_info"] == "nc overridden.connection 1337"

            # ...and so should the rendered view template
            assert "nc overridden.connection 1337" in data["view"]

            # Model-backed properties (e.g. html) must still render correctly
            assert "read override description" in data["view"]

            # The admin preview renders the same view template and should
            # receive the read() output as well
            r = admin_client.get(f"/admin/challenges/preview/{challenge_id}")
            assert r.status_code == 200
            assert b"nc overridden.connection 1337" in r.data
        finally:
            del CHALLENGE_CLASSES["read_override"]
    destroy_ctfd(app)


def test_standard_challenge_render_unchanged():
    """Test that the default challenge types still render without read() overrides"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        admin_client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "standard_name",
            "category": "category",
            "description": "standard description",
            "value": 100,
            "state": "visible",
            "type": "standard",
        }
        r = admin_client.post("/api/v1/challenges", json=challenge_data)
        assert r.status_code == 200
        challenge_id = r.get_json()["data"]["id"]

        user_client = login_as_user(app)
        r = user_client.get(f"/api/v1/challenges/{challenge_id}")
        assert r.status_code == 200
        data = r.get_json()["data"]
        assert data["name"] == "standard_name"
        assert "standard description" in data["view"]
    destroy_ctfd(app)
