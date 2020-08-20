#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
    login_as_user,
    register_user,
)


def test_admin_view_fields():
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        gen_field(
            app.db, name="CustomField1", required=True, public=True, editable=True
        )
        gen_field(
            app.db, name="CustomField2", required=False, public=True, editable=True
        )
        gen_field(
            app.db, name="CustomField3", required=False, public=False, editable=True
        )
        gen_field(
            app.db, name="CustomField4", required=False, public=False, editable=False
        )

        with login_as_user(app, name="admin") as admin:
            # Admins should see all user fields regardless of public or editable
            r = admin.get("/admin/users/2")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" in resp
    destroy_ctfd(app)
