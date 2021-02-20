#!/usr/bin/env python
# -*- coding: utf-8 -*-
from freezegun import freeze_time

from CTFd.exceptions import TeamTokenExpiredException, TeamTokenInvalidException
from CTFd.models import Teams, Users
from CTFd.utils import set_config
from tests.helpers import create_ctfd, destroy_ctfd, gen_team, gen_user, login_as_user


def test_team_invite_codes():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team1 = gen_team(app.db, name="team1", email="team1@examplectf.com")
        with freeze_time("2017-10-7 00:00:00"):
            invite_code = team1.get_invite_code()
            team = Teams.load_invite_code(invite_code)
            assert team.id == team1.id

        with freeze_time("2017-10-8 00:00:01"):
            try:
                team = Teams.load_invite_code(invite_code)
            except TeamTokenExpiredException:
                # This token should be expired and we shouldn't get a team object back
                pass
            else:
                print("Token should have expired")
                raise Exception

        # Change team's password
        team.password = "new_test_password"
        app.db.session.commit()

        with freeze_time("2017-10-7 00:00:00"):
            try:
                team = Teams.load_invite_code(invite_code)
            except TeamTokenInvalidException:
                pass
            else:
                print("Token should have been invalidated by password change")
                raise Exception
    destroy_ctfd(app)


def test_api_user_facing_invite_tokens():
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        team1 = gen_team(app.db, name="team1", email="team1@examplectf.com")
        user = team1.captain
        with login_as_user(app, name=user.name) as captain:
            r = captain.post("/api/v1/teams/me/members", json="")
            invite_code = r.get_json()["data"]["code"]
            assert invite_code

        new_user = gen_user(app.db)
        with login_as_user(app, name=new_user.name) as user:
            url = f"/teams/invite?code={invite_code}"
            user.get(url)
            with user.session_transaction() as sess:
                data = {
                    "nonce": sess.get("nonce"),
                }
            r = user.post(url, data=data)
            assert r.status_code == 302
            assert r.location.endswith("/challenges")
        assert Users.query.filter_by(id=new_user.id).first().team_id == team1.id

        # Test team size limits
        set_config("team_size", 1)
        new_user2 = gen_user(app.db, name="new_user2", email="new_user2@examplectf.com")
        with login_as_user(app, name=new_user2.name) as user:
            url = f"/teams/invite?code={invite_code}"
            user.get(url)
            with user.session_transaction() as sess:
                data = {
                    "nonce": sess.get("nonce"),
                }
            r = user.post(url, data=data)
            assert r.status_code == 403
            assert "has already reached the team size limit" in r.get_data(as_text=True)
    destroy_ctfd(app)
