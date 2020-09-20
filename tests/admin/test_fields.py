#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_field,
    gen_team,
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


def test_admin_view_team_fields():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
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

        with login_as_user(app, name="admin") as admin:
            # Admins should see all team fields regardless of public or editable
            r = admin.get("/admin/teams/1")
            resp = r.get_data(as_text=True)
            assert "CustomField1" in resp
            assert "CustomField2" in resp
            assert "CustomField3" in resp
            assert "CustomField4" in resp
    destroy_ctfd(app)
