#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users
from CTFd.utils.user import is_admin, get_current_user
from CTFd.utils.security.auth import login_user
from tests.helpers import create_ctfd, destroy_ctfd, register_user

from CTFd.cache import clear_user_session


def test_clear_user_session():
    app = create_ctfd()
    with app.app_context():
        register_user(app)

        # Users by default should have a non-admin type
        user = Users.query.filter_by(id=2).first()
        with app.test_request_context("/"):
            login_user(user)
            user = get_current_user()
            assert user.id == 2
            assert user.type == "user"
            assert is_admin() is False

        # Set the user's updated type
        user = Users.query.filter_by(id=2).first()
        user.type = "admin"
        app.db.session.commit()

        # The user's type should now be admin
        user = Users.query.filter_by(id=2).first()
        with app.test_request_context("/"):
            login_user(user)
            user = get_current_user()
            assert user.id == 2
            assert user.type == "admin"
            assert is_admin() is True
    destroy_ctfd(app)
