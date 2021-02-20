#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Fields, TeamFieldEntries, Teams, UserFieldEntries, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
    gen_team,
    login_as_user,
    register_user,
)


def test_api_custom_fields():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_field(app.db, name="CustomField1")
        gen_field(app.db, name="CustomField2")

        with login_as_user(app) as user:
            r = user.get("/api/v1/configs/fields", json="")
            assert r.status_code == 403

        with login_as_user(app, name="admin") as admin:
            r = admin.get("/api/v1/configs/fields", json="")
            resp = r.get_json()

            assert resp == {
                "success": True,
                "data": [
                    {
                        "public": True,
                        "required": True,
                        "type": "user",
                        "editable": True,
                        "id": 1,
                        "field_type": "text",
                        "description": "CustomFieldDescription",
                        "name": "CustomField1",
                    },
                    {
                        "public": True,
                        "required": True,
                        "type": "user",
                        "editable": True,
                        "id": 2,
                        "field_type": "text",
                        "description": "CustomFieldDescription",
                        "name": "CustomField2",
                    },
                ],
            }

            r = admin.post(
                "/api/v1/configs/fields",
                json={
                    "public": True,
                    "required": True,
                    "editable": True,
                    "id": 2,
                    "type": "user",
                    "field_type": "text",
                    "description": "CustomFieldDescription",
                    "name": "CustomField3",
                },
            )
            assert r.status_code == 200

            r = admin.get("/api/v1/configs/fields", json="")
            resp = r.get_json()
            assert resp == {
                "success": True,
                "data": [
                    {
                        "public": True,
                        "required": True,
                        "type": "user",
                        "editable": True,
                        "id": 1,
                        "field_type": "text",
                        "description": "CustomFieldDescription",
                        "name": "CustomField1",
                    },
                    {
                        "public": True,
                        "required": True,
                        "type": "user",
                        "editable": True,
                        "id": 2,
                        "field_type": "text",
                        "description": "CustomFieldDescription",
                        "name": "CustomField2",
                    },
                    {
                        "public": True,
                        "required": True,
                        "editable": True,
                        "id": 3,
                        "type": "user",
                        "field_type": "text",
                        "description": "CustomFieldDescription",
                        "name": "CustomField3",
                    },
                ],
            }

            r = admin.patch(
                "/api/v1/configs/fields/3",
                json={
                    "public": False,
                    "required": False,
                    "editable": False,
                    "id": 4,
                    "type": "user",
                    "field_type": "text",
                    "description": "CustomFieldDescription",
                    "name": "PatchedCustomField3",
                },
            )
            assert r.status_code == 200
            assert r.get_json()["data"] == {
                "public": False,
                "required": False,
                "editable": False,
                "id": 3,
                "type": "user",
                "field_type": "text",
                "description": "CustomFieldDescription",
                "name": "PatchedCustomField3",
            }

            r = admin.get("/api/v1/configs/fields/3", json="")
            assert r.status_code == 200
            assert r.get_json()["data"] == {
                "public": False,
                "required": False,
                "editable": False,
                "id": 3,
                "type": "user",
                "field_type": "text",
                "description": "CustomFieldDescription",
                "name": "PatchedCustomField3",
            }

            r = admin.delete("/api/v1/configs/fields/3", json="")
            assert r.status_code == 200

            r = admin.get("/api/v1/configs/fields/3", json="")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_api_self_fields_permissions():
    app = create_ctfd()
    with app.app_context():
        gen_field(app.db, name="CustomField1", public=False, editable=False)
        gen_field(app.db, name="CustomField2", public=True, editable=True)

        with app.test_client() as client:
            client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                    "fields[1]": "CustomValue1",
                    "fields[2]": "CustomValue2",
                }
            r = client.post("/register", data=data)
            with client.session_transaction() as sess:
                assert sess["id"]

        with login_as_user(app) as user, login_as_user(app, name="admin") as admin:
            r = user.get("/api/v1/users/me")
            resp = r.get_json()
            assert resp["data"]["fields"] == [
                {
                    "value": "CustomValue2",
                    "name": "CustomField2",
                    "description": "CustomFieldDescription",
                    "type": "text",
                    "field_id": 2,
                }
            ]

            r = admin.get("/api/v1/users/2")
            resp = r.get_json()
            assert len(resp["data"]["fields"]) == 2

            field = Fields.query.filter_by(id=1).first()
            field.public = True
            app.db.session.commit()
            r = user.get("/api/v1/users/me")
            resp = r.get_json()
            assert len(resp["data"]["fields"]) == 2

    destroy_ctfd(app)


def test_partial_field_update():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        gen_field(app.db, name="CustomField1")
        gen_field(app.db, name="CustomField2")

        with login_as_user(app) as user:
            r = user.patch(
                "/api/v1/users/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomValue1"},
                        {"field_id": 2, "value": "CustomValue2"},
                    ]
                },
            )
            assert r.status_code == 200
            assert UserFieldEntries.query.count() == 2

            r = user.patch(
                "/api/v1/users/me",
                json={"fields": [{"field_id": 2, "value": "NewCustomValue2"}]},
            )
            assert r.status_code == 200
            assert UserFieldEntries.query.count() == 2
            assert (
                UserFieldEntries.query.filter_by(field_id=1, user_id=2).first().value
                == "CustomValue1"
            )
            assert (
                UserFieldEntries.query.filter_by(field_id=2, user_id=2).first().value
                == "NewCustomValue2"
            )

        with login_as_user(app, name="admin") as admin:
            r = admin.patch(
                "/api/v1/users/2",
                json={"fields": [{"field_id": 2, "value": "AdminNewCustomValue2"}]},
            )
            assert r.status_code == 200
            assert UserFieldEntries.query.count() == 2
            assert (
                UserFieldEntries.query.filter_by(field_id=1, user_id=2).first().value
                == "CustomValue1"
            )
            assert (
                UserFieldEntries.query.filter_by(field_id=2, user_id=2).first().value
                == "AdminNewCustomValue2"
            )

    destroy_ctfd(app)


def test_api_team_self_fields_permissions():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        app.db.session.commit()
        team = Teams.query.filter_by(id=1).first()
        team.captain_id = 2
        app.db.session.commit()

        gen_field(
            app.db, name="CustomField1", type="team", public=False, editable=False
        )
        gen_field(app.db, name="CustomField2", type="team", public=True, editable=True)

        app.db.session.add(
            TeamFieldEntries(type="team", value="CustomValue1", team_id=1, field_id=1)
        )
        app.db.session.add(
            TeamFieldEntries(type="team", value="CustomValue2", team_id=1, field_id=2)
        )
        app.db.session.commit()

        assert len(team.field_entries) == 2

        with login_as_user(app) as user, login_as_user(app, name="admin") as admin:
            r = user.get("/api/v1/teams/me")
            resp = r.get_json()
            assert resp["data"]["fields"] == [
                {
                    "value": "CustomValue2",
                    "name": "CustomField2",
                    "description": "CustomFieldDescription",
                    "type": "text",
                    "field_id": 2,
                }
            ]
            assert len(resp["data"]["fields"]) == 1

            # Admin gets data and should see all fields
            r = admin.get("/api/v1/teams/1")
            resp = r.get_json()
            assert len(resp["data"]["fields"]) == 2

            r = user.patch(
                "/api/v1/teams/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "NewCustomValue1"},
                        {"field_id": 2, "value": "NewCustomValue2"},
                    ]
                },
            )
            assert r.get_json() == {
                "success": False,
                "errors": {"fields": ["Field 'CustomField1' cannot be editted"]},
            }
            assert r.status_code == 400
            assert (
                TeamFieldEntries.query.filter_by(id=1).first().value == "CustomValue1"
            )
            assert (
                TeamFieldEntries.query.filter_by(id=2).first().value == "CustomValue2"
            )

            # After making the field public the user should see both fields
            field = Fields.query.filter_by(id=1).first()
            field.public = True
            app.db.session.commit()
            r = user.get("/api/v1/teams/me")
            resp = r.get_json()
            assert len(resp["data"]["fields"]) == 2

            # Captain should be able to edit their values after it's made editable
            field = Fields.query.filter_by(id=1).first()
            field.editable = True
            app.db.session.commit()
            r = user.patch(
                "/api/v1/teams/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "NewCustomValue1"},
                        {"field_id": 2, "value": "NewCustomValue2"},
                    ]
                },
            )
            print(r.get_json())
            assert r.status_code == 200
            assert (
                TeamFieldEntries.query.filter_by(id=1).first().value
                == "NewCustomValue1"
            )
            assert (
                TeamFieldEntries.query.filter_by(id=2).first().value
                == "NewCustomValue2"
            )
    destroy_ctfd(app)


def test_team_partial_field_update():
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
        gen_field(app.db, name="CustomField2", type="team")

        with login_as_user(app) as user:
            r = user.patch(
                "/api/v1/teams/me",
                json={
                    "fields": [
                        {"field_id": 1, "value": "CustomValue1"},
                        {"field_id": 2, "value": "CustomValue2"},
                    ]
                },
            )
            assert r.status_code == 200
            assert TeamFieldEntries.query.count() == 2

            r = user.patch(
                "/api/v1/teams/me",
                json={"fields": [{"field_id": 2, "value": "NewCustomValue2"}]},
            )
            assert r.status_code == 200
            assert TeamFieldEntries.query.count() == 2
            assert (
                TeamFieldEntries.query.filter_by(field_id=1, team_id=1).first().value
                == "CustomValue1"
            )
            assert (
                TeamFieldEntries.query.filter_by(field_id=2, team_id=1).first().value
                == "NewCustomValue2"
            )

        with login_as_user(app, name="admin") as admin:
            r = admin.patch(
                "/api/v1/teams/1",
                json={"fields": [{"field_id": 2, "value": "AdminNewCustomValue2"}]},
            )
            assert r.status_code == 200
            assert TeamFieldEntries.query.count() == 2
            assert (
                TeamFieldEntries.query.filter_by(field_id=1, team_id=1).first().value
                == "CustomValue1"
            )
            assert (
                TeamFieldEntries.query.filter_by(field_id=2, team_id=1).first().value
                == "AdminNewCustomValue2"
            )

    destroy_ctfd(app)
