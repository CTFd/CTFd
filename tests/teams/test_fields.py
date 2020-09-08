#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import TeamFieldEntries, Teams, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
    gen_team,
    login_as_user,
    register_user,
)


def test_new_fields_show_on_pages():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        team = Teams.query.filter_by(id=1).first()
        team.captain_id = 2
        app.db.session.commit()

        gen_field(app.db, name="CustomField1", type="team")

        with login_as_user(app) as client:
            r = client.get("/teams/new")
            assert "CustomField1" in r.get_data(as_text=True)
            assert "CustomFieldDescription" in r.get_data(as_text=True)

            r = client.get("/team")
            assert "CustomField1" in r.get_data(as_text=True)
            assert "CustomFieldDescription" in r.get_data(as_text=True)

            r = client.patch(
                "/api/v1/teams/me",
                json={"fields": [{"field_id": 1, "value": "CustomFieldEntry"}]},
            )
            resp = r.get_json()
            assert resp["success"] is True
            assert resp["data"]["fields"][0]["value"] == "CustomFieldEntry"
            assert resp["data"]["fields"][0]["description"] == "CustomFieldDescription"
            assert resp["data"]["fields"][0]["name"] == "CustomField1"
            assert resp["data"]["fields"][0]["field_id"] == 1

            r = client.get("/team")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomFieldEntry" in resp

            r = client.get("/teams/1")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomFieldEntry" in resp
    destroy_ctfd(app)


def test_team_fields_required_on_creation():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        gen_field(app.db, type="team")

        with app.app_context():
            with login_as_user(app) as client:
                assert Teams.query.count() == 0
                r = client.get("/teams/new")
                resp = r.get_data(as_text=True)
                assert "CustomField" in resp
                assert "CustomFieldDescription" in resp

                with client.session_transaction() as sess:
                    data = {
                        "name": "team",
                        "password": "password",
                        "nonce": sess.get("nonce"),
                    }
                r = client.post("/teams/new", data=data)
                assert "Please provide all required fields" in r.get_data(as_text=True)
                assert Teams.query.count() == 0

                with client.session_transaction() as sess:
                    data = {
                        "name": "team",
                        "password": "password",
                        "fields[1]": "CustomFieldEntry",
                        "nonce": sess.get("nonce"),
                    }
                r = client.post("/teams/new", data=data)
                assert r.status_code == 302
                assert Teams.query.count() == 1

                entry = TeamFieldEntries.query.filter_by(id=1).first()
                assert entry.team_id == 1
                assert entry.value == "CustomFieldEntry"
    destroy_ctfd(app)


def test_team_fields_properties():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        team = Teams.query.filter_by(id=1).first()
        team.captain_id = 2
        app.db.session.commit()

        gen_field(
            app.db,
            name="CustomField1",
            type="team",
            required=True,
            public=True,
            editable=True,
        )
        gen_field(
            app.db,
            name="CustomField2",
            type="team",
            required=False,
            public=True,
            editable=True,
        )
        gen_field(
            app.db,
            name="CustomField3",
            type="team",
            required=False,
            public=False,
            editable=True,
        )
        gen_field(
            app.db,
            name="CustomField4",
            type="team",
            required=False,
            public=False,
            editable=False,
        )

        with login_as_user(app) as client:
            r = client.get("/teams/new")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" in resp

            r = client.get("/team")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" not in resp

            r = client.patch(
                "/api/v1/teams/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomFieldEntry1"},
                        {"field_id": 2, "value": "CustomFieldEntry2"},
                        {"field_id": 3, "value": "CustomFieldEntry3"},
                        {"field_id": 4, "value": "CustomFieldEntry4"},
                    ]
                },
            )
            resp = r.get_json()
            assert resp == {
                "success": False,
                "errors": {"fields": ["Field 'CustomField4' cannot be editted"]},
            }

            r = client.patch(
                "/api/v1/teams/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomFieldEntry1"},
                        {"field_id": 2, "value": "CustomFieldEntry2"},
                        {"field_id": 3, "value": "CustomFieldEntry3"},
                    ]
                },
            )
            assert r.status_code == 200

            r = client.get("/team")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert (
                "CustomField3" in resp
            )  # This is here because /team contains team settings
            assert "CustomField4" not in resp

            r = client.get("/teams/1")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" not in resp
            assert "CustomField4" not in resp
    destroy_ctfd(app)


def test_teams_boolean_checkbox_field():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        gen_field(
            app.db,
            name="CustomField1",
            type="team",
            field_type="boolean",
            required=False,
        )

        with login_as_user(app) as client:
            r = client.get("/teams/new")
            resp = r.get_data(as_text=True)

            # We should have rendered a checkbox input
            assert "checkbox" in resp

            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                    "fields[1]": "y",
                }
            client.post("/teams/new", data=data)
            assert Teams.query.count() == 1

        assert TeamFieldEntries.query.count() == 1
        assert TeamFieldEntries.query.filter_by(id=1).first().value is True

        with login_as_user(app) as client:
            r = client.get("/team")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "checkbox" in resp

            r = client.patch(
                "/api/v1/teams/me", json={"fields": [{"field_id": 1, "value": False}]}
            )
            assert r.status_code == 200
            assert TeamFieldEntries.query.count() == 1
            assert TeamFieldEntries.query.filter_by(id=1).first().value is False
    destroy_ctfd(app)
