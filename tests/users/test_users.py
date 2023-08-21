#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    login_as_user,
    register_user,
)


def test_accessing_hidden_users():
    """Hidden users should not give any data from /users or /api/v1/users"""
    app = create_ctfd()
    with app.app_context():
        register_user(
            app, name="visible_user", email="visible_user@examplectf.com"
        )  # ID 2
        register_user(
            app, name="hidden_user", email="hidden_user@examplectf.com"
        )  # ID 3
        register_user(
            app, name="banned_user", email="banned_user@examplectf.com"
        )  # ID 4
        user = Users.query.filter_by(name="hidden_user").first()
        user.hidden = True
        app.db.session.commit()
        user = Users.query.filter_by(name="banned_user").first()
        user.banned = True
        app.db.session.commit()

        with login_as_user(app, name="visible_user") as client:
            assert client.get("/users/3").status_code == 404
            assert client.get("/api/v1/users/3").status_code == 404
            assert client.get("/api/v1/users/3/solves").status_code == 404
            assert client.get("/api/v1/users/3/fails").status_code == 404
            assert client.get("/api/v1/users/3/awards").status_code == 404

            assert client.get("/users/4").status_code == 404
            assert client.get("/api/v1/users/4").status_code == 404
            assert client.get("/api/v1/users/4/solves").status_code == 404
            assert client.get("/api/v1/users/4/fails").status_code == 404
            assert client.get("/api/v1/users/4/awards").status_code == 404
    destroy_ctfd(app)


def test_hidden_user_visibility():
    """Hidden users should not show up on /users or /api/v1/users or /api/v1/scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="hidden_user")

        with login_as_user(app, name="hidden_user") as client:
            user = Users.query.filter_by(id=2).first()
            user_id = user.id
            user_name = user.name
            user.hidden = True
            app.db.session.commit()

            r = client.get("/users")
            response = r.get_data(as_text=True)
            # Only search in body content
            body_start = response.find("<body>")
            body_end = response.find("</body>")
            response = response[body_start:body_end]
            assert user_name not in response

            r = client.get("/api/v1/users")
            response = r.get_json()
            assert user_name not in response

            gen_award(app.db, user_id)

            r = client.get("/scoreboard")
            response = r.get_data(as_text=True)
            # Only search in body content
            body_start = response.find("<body>")
            body_end = response.find("</body>")
            response = response[body_start:body_end]
            assert user_name not in response

            r = client.get("/api/v1/scoreboard")
            response = r.get_json()
            assert user_name not in response

            # User should re-appear after disabling hiding
            # Use an API call to cause a cache clear
            with login_as_user(app, name="admin") as admin:
                r = admin.patch("/api/v1/users/2", json={"hidden": False})
                assert r.status_code == 200

            r = client.get("/users")
            response = r.get_data(as_text=True)
            # Only search in body content
            body_start = response.find("<body>")
            body_end = response.find("</body>")
            response = response[body_start:body_end]
            assert user_name in response

            r = client.get("/api/v1/users")
            response = r.get_data(as_text=True)
            assert user_name in response

            r = client.get("/api/v1/scoreboard")
            response = r.get_data(as_text=True)
            assert user_name in response
    destroy_ctfd(app)


def test_num_users_limit():
    """Only num_users users can be created"""
    app = create_ctfd()
    with app.app_context():
        set_config("num_users", 1)

        register_user(app)
        with app.test_client() as client:
            r = client.get("/register")
            assert r.status_code == 403

            # team should be blocked from creation
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/register", data=data)
            resp = r.get_data(as_text=True)
            # This number is 2 to account for the admin and the registered user
            assert Users.query.count() == 2
            assert "Reached the maximum number of users" in resp

            # Can the team be created after the num has been bumped
            set_config("num_users", 2)
            with client.session_transaction() as sess:
                data = {
                    "name": "user1",
                    "email": "user1@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            r = client.post("/register", data=data)
            resp = r.get_data(as_text=True)
            assert r.status_code == 302
            assert Users.query.count() == 3
    destroy_ctfd(app)
