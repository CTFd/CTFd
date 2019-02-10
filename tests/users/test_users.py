#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *


def test_hidden_user_visibility():
    """Hidden users should not show up on /users or /api/v1/users or /api/v1/scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="hidden_user")

        with login_as_user(app, name="hidden_user") as client:
            user = Users.query.filter_by(id=2).first()
            user_name = user.name
            user.hidden = True
            app.db.session.commit()

            r = client.get('/users')
            response = r.get_data(as_text=True)
            assert user_name not in response

            r = client.get('/api/v1/users')
            response = r.get_json()
            assert user_name not in response

            gen_award(app.db, user.id)

            r = client.get('/scoreboard')
            response = r.get_data(as_text=True)
            assert user_name not in response

            r = client.get('/api/v1/scoreboard')
            response = r.get_json()
            assert user_name not in response

            # User should re-appear after disabling hiding
            # Use an API call to cause a cache clear
            with login_as_user(app, name='admin') as admin:
                r = admin.patch('/api/v1/users/2', json={
                    "hidden": False,
                })
                assert r.status_code == 200

            r = client.get('/users')
            response = r.get_data(as_text=True)
            assert user_name in response

            r = client.get('/api/v1/users')
            response = r.get_data(as_text=True)
            assert user_name in response

            r = client.get('/api/v1/scoreboard')
            response = r.get_data(as_text=True)
            assert user_name in response
    destroy_ctfd(app)
