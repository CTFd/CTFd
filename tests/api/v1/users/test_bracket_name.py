#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Users, Brackets, db
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user, register_user


def test_api_users_me_includes_bracket_name():
    """GET /api/v1/users/me should include bracket name when user has a bracket"""
    app = create_ctfd()
    with app.app_context():
        # Create a bracket first
        bracket = Brackets(name="Test Bracket", description="A test bracket", type="users")
        db.session.add(bracket)
        db.session.commit()
        
        # Register a user with raise_for_error=False to avoid assertion errors
        register_user(app, name="user", email="user@examplectf.com", password="password", raise_for_error=False)
        user = Users.query.filter_by(name="user").first()
        
        # Ensure user was created
        if not user:
            # If registration failed, create user manually
            user = Users(name="user", email="user@examplectf.com", password="password")
            db.session.add(user)
            db.session.commit()
        
        # Assign bracket to user
        user.bracket_id = bracket.id
        db.session.commit()
        
        with login_as_user(app, "user") as client:
            r = client.get("/api/v1/users/me")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["success"] is True
            assert "data" in resp
            
            user_data = resp["data"]
            assert "bracket_id" in user_data
            assert "bracket" in user_data
            assert user_data["bracket_id"] == bracket.id
            assert user_data["bracket"] == "Test Bracket"
    
    destroy_ctfd(app)


def test_api_users_me_without_bracket():
    """GET /api/v1/users/me should not include bracket name when user has no bracket"""
    app = create_ctfd()
    with app.app_context():
        # Register a user without a bracket
        register_user(app, name="user", email="user@examplectf.com", password="password")
        
        with login_as_user(app, "user") as client:
            r = client.get("/api/v1/users/me")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["success"] is True
            assert "data" in resp
            
            user_data = resp["data"]
            assert user_data.get("bracket_id") is None
            # Bracket name should not be included when no bracket is assigned
            assert "bracket" not in user_data
    
    destroy_ctfd(app)