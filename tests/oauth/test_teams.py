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


def test_num_teams_limit():
    """Only num_teams teams can be created even via MLC"""
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
        set_config("num_teams", 1)
        gen_team(app.db, member_count=1, oauth_id=1234)
        login_with_mlc(
            app,
            name="foobar",
            email="foobar@a.com",
            oauth_id=111,
            team_name="foobar",
            team_oauth_id=1111,
            raise_for_error=False,
        )
        assert Teams.query.count() == 1

        set_config("num_teams", 2)
        login_with_mlc(
            app,
            name="foobarbaz",
            email="foobarbaz@a.com",
            oauth_id=222,
            team_name="foobarbaz",
            team_oauth_id=2222,
        )
        assert Teams.query.count() == 2
    destroy_ctfd(app)
