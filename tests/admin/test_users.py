#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_tracking,
    gen_user,
    login_as_user,
)


def test_admin_user_ip_search():
    """Can an admin search user IPs"""
    app = create_ctfd()
    with app.app_context():
        u1 = gen_user(app.db, name="user1", email="user1@examplectf.com")
        gen_tracking(app.db, user_id=u1.id, ip="1.1.1.1")

        u2 = gen_user(app.db, name="user2", email="user2@examplectf.com")
        gen_tracking(app.db, user_id=u2.id, ip="2.2.2.2")

        u3 = gen_user(app.db, name="user3", email="user3@examplectf.com")
        gen_tracking(app.db, user_id=u3.id, ip="3.3.3.3")

        u4 = gen_user(app.db, name="user4", email="user4@examplectf.com")
        gen_tracking(app.db, user_id=u4.id, ip="3.3.3.3")
        gen_tracking(app.db, user_id=u4.id, ip="4.4.4.4")

        with login_as_user(app, name="admin", password="password") as admin:
            r = admin.get("/admin/users?field=ip&q=1.1.1.1")
            resp = r.get_data(as_text=True)
            assert "user1" in resp
            assert "user2" not in resp
            assert "user3" not in resp

            r = admin.get("/admin/users?field=ip&q=2.2.2.2")
            resp = r.get_data(as_text=True)
            assert "user1" not in resp
            assert "user2" in resp
            assert "user3" not in resp

            r = admin.get("/admin/users?field=ip&q=3.3.3.3")
            resp = r.get_data(as_text=True)
            assert "user1" not in resp
            assert "user2" not in resp
            assert "user3" in resp
            assert "user4" in resp
    destroy_ctfd(app)


def test_admin_user_status_filter():
    """Can an admin filter users by status"""
    app = create_ctfd()
    with app.app_context():
        u1 = gen_user(app.db, name="active_user", email="active@examplectf.com")
        u2 = gen_user(
            app.db, name="banned_user", email="banned@examplectf.com", banned=True
        )
        u3 = gen_user(
            app.db, name="hidden_user", email="hidden@examplectf.com", hidden=True
        )
        u4 = gen_user(
            app.db,
            name="unverified_user",
            email="unverified@examplectf.com",
            verified=False,
        )

        with login_as_user(app, name="admin", password="password") as admin:
            # Filter by banned
            r = admin.get("/admin/users?status=banned")
            resp = r.get_data(as_text=True)
            assert "banned_user" in resp
            assert "active_user" not in resp
            assert "hidden_user" not in resp

            # Filter by hidden
            r = admin.get("/admin/users?status=hidden")
            resp = r.get_data(as_text=True)
            assert "hidden_user" in resp
            assert "active_user" not in resp
            assert "banned_user" not in resp

            # Filter by unverified
            r = admin.get("/admin/users?status=unverified")
            resp = r.get_data(as_text=True)
            assert "unverified_user" in resp
            assert "active_user" not in resp
            assert "banned_user" not in resp

            # Filter by active - should exclude banned and hidden
            r = admin.get("/admin/users?status=active")
            resp = r.get_data(as_text=True)
            assert "active_user" in resp
            assert "banned_user" not in resp
            assert "hidden_user" not in resp
    destroy_ctfd(app)
