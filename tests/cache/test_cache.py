#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.cache import clear_all_user_sessions, clear_user_session
from CTFd.models import Users
from CTFd.utils.security.auth import login_user
from CTFd.utils.user import get_current_user, is_admin
from tests.helpers import create_ctfd, destroy_ctfd, register_user


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

            # Should still return False because this is still cached
            assert is_admin() is False

            clear_user_session(user_id=2)

            # Should now return True after clearing cache
            assert is_admin() is True
    destroy_ctfd(app)


def test_clear_all_user_sessions():
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

            # Should still return False because this is still cached
            assert is_admin() is False

            clear_all_user_sessions()

            # Should now return True after clearing cache
            assert is_admin() is True
    destroy_ctfd(app)
