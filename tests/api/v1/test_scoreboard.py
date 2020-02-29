#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.cache import clear_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_solve,
    login_as_user,
    register_user,
)


def test_scoreboard_is_cached():
    """Test that /api/v1/scoreboard is properly cached and cleared"""
    app = create_ctfd()
    with app.app_context():
        # create user1
        register_user(app, name="user1", email="user1@ctfd.io")

        # create challenge
        chal = gen_challenge(app.db, value=100)
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        chal_id = chal.id

        # create a solve for the challenge for user1. (the id is 2 because of the admin)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        with login_as_user(app, "user1") as client:
            # No cached data
            assert app.cache.get("view/api.scoreboard_scoreboard_list") is None
            assert app.cache.get("view/api.scoreboard_scoreboard_detail") is None

            # Load and check cached data
            client.get("/api/v1/scoreboard")
            assert app.cache.get("view/api.scoreboard_scoreboard_list")
            client.get("/api/v1/scoreboard/top/10")
            assert app.cache.get("view/api.scoreboard_scoreboard_detail")

            # Check scoreboard page
            assert app.cache.get("view/scoreboard.listing") is None
            client.get("/scoreboard")
            assert app.cache.get("view/scoreboard.listing")

            # Empty standings and check that the cached data is gone
            clear_standings()
            assert app.cache.get("view/api.scoreboard_scoreboard_list") is None
            assert app.cache.get("view/api.scoreboard_scoreboard_detail") is None
            assert app.cache.get("view/scoreboard.listing") is None
    destroy_ctfd(app)
