#!/usr/bin/env python
# -*- coding: utf-8 -*-
from CTFd.models import Teams
from CTFd.utils import set_config
from tests.helpers import create_ctfd, destroy_ctfd, gen_team, login_with_mlc


def test_team_size_limit():
    """Only team_size amount of members can join a team even via MLC"""
    app = create_ctfd(user_mode="teams")
    app.config.update(
        {
            "OAUTH_CLIENT_ID": "ctfd_testing_client_id",
            "OAUTH_CLIENT_SECRET": "ctfd_testing_client_secret",
            "OAUTH_AUTHORIZATION_ENDPOINT": "http://auth.localhost/oauth/authorize",
            "OAUTH_TOKEN_ENDPOINT": "http://auth.localhost/oauth/token",
            "OAUTH_API_ENDPOINT": "http://api.localhost/user",
        }
    )
    with app.app_context():
        set_config("team_size", 1)
        team = gen_team(app.db, member_count=1, oauth_id=1234)
        team_id = team.id
        login_with_mlc(
            app, team_name="team_name", team_oauth_id=1234, raise_for_error=False
        )
        assert len(Teams.query.filter_by(id=team_id).first().members) == 1

        set_config("team_size", 2)
        login_with_mlc(app, team_name="team_name", team_oauth_id=1234)
        assert len(Teams.query.filter_by(id=team_id).first().members) == 2
    destroy_ctfd(app)
