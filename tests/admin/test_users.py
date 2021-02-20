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
