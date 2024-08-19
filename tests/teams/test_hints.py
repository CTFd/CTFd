#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils.scores import get_standings
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_award,
    gen_challenge,
    gen_hint,
    gen_team,
    gen_user,
    login_as_user,
)


def test_hint_team_unlock():
    """Is a user's unlocked hint reflected on other team members"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        second_user = gen_user(app.db, name="user", email="second@examplectf.com")
        team = gen_team(app.db)
        user.team_id = team.id
        second_user.team_id = team.id
        team.members.append(user)
        team.members.append(second_user)
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="hint", cost=1, type="standard")
        # Give the points to the user that doesn't unlock
        # Users that unlock hints should be able to unlock but cost their team points
        gen_award(app.db, user_id=3, team_id=team.id)
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            # Assert that we don't see a hint
            r = client.get("/api/v1/hints/1")
            assert r.get_json()["data"].get("content") is None

            # Unlock the hint
            client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})

            # Assert that we see a hint
            r = client.get("/api/v1/hints/1")
            assert r.get_json()["data"].get("content")
        with login_as_user(app) as second_client:
            # Assert that we see a hint
            r = second_client.get("/api/v1/hints/1")
            assert r.get_json()["data"].get("content")

            # Assert that we can't double unlock
            r = second_client.post(
                "/api/v1/unlocks", json={"target": 1, "type": "hints"}
            )
            assert r.status_code == 400
            assert (
                r.get_json()["errors"]["target"]
                == "You've already unlocked this target"
            )

            # Assert that we see a hint
            r = second_client.get("/api/v1/hints/1")
            assert r.json["data"]["content"] == "hint"

            # Verify standings
            # We start with 100 points from the award.
            # We lose a point because we unlock successfully once
            standings = get_standings()
            assert standings[0].name == "team_name"
            assert standings[0].score == 99
    destroy_ctfd(app)


def test_hint_team_unlocking_without_points():
    """Test that teams cannot enter negative point valuations from unlocking hints"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        user = gen_user(app.db)
        second_user = gen_user(app.db, name="user", email="second@examplectf.com")
        team = gen_team(app.db)
        user.team_id = team.id
        second_user.team_id = team.id
        team.members.append(user)
        team.members.append(second_user)
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="hint", cost=1, type="standard")
        app.db.session.commit()
        with login_as_user(app, name="user_name") as client:
            # Assert that we don't see a hint
            r = client.get("/api/v1/hints/1")
            assert r.get_json()["data"].get("content") is None

            # Attempt to unlock the hint
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 400
            assert (
                r.get_json()["errors"]["score"]
                == "You do not have enough points to unlock this hint"
            )
    destroy_ctfd(app)


def test_teams_dont_prevent_other_teams_from_unlocking_hints():
    """Unlocks from one user don't affect other users"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        chal = gen_challenge(app.db)
        gen_hint(app.db, chal.id, content="This is a hint", cost=1, type="standard")

        team1 = gen_team(app.db, name="team1", email="team1@examplectf.com")
        team2 = gen_team(app.db, name="team2", email="team2@examplectf.com")

        # Give users points with an award
        gen_award(app.db, user_id=team1.captain_id)
        gen_award(app.db, user_id=team2.captain_id)

        captain1 = team1.captain.name
        captain2 = team2.captain.name

        app.db.session.commit()

        # First team unlocks hint
        with login_as_user(app, name=captain1) as client:
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200

        # Second team unlocks hint
        with login_as_user(app, name=captain2) as client:
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
            r = client.post("/api/v1/unlocks", json={"target": 1, "type": "hints"})
            assert r.status_code == 200
            r = client.get("/api/v1/hints/1")
            assert r.status_code == 200
    destroy_ctfd(app)
