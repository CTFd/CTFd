#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
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

            r = admin.get("/api/v1/configs/fields/3")
            assert r.status_code == 200
            assert r.get_json()["data"] == {
                "public": False,
                "required": False,
                "editable": False,
                "type": "user",
                "field_type": "text",
                "description": "CustomFieldDescription",
                "name": "PatchedCustomField3",
            }

            r = admin.delete("/api/v1/configs/fields/3")
            assert r.status_code == 200

            r = admin.get("/api/v1/configs/fields/3")
            assert r.status_code == 404
    destroy_ctfd(app)
