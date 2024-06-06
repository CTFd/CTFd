#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataclasses

import pytest

from CTFd.models import Challenges, Solves, Users
from CTFd.plugins.challenges import BaseChallenge
from tests.helpers import create_ctfd, destroy_ctfd, gen_challenge, gen_flag, gen_team


@dataclasses.dataclass
class FakeRequest:
    form: dict[str, str]
    access_route: list[str] = dataclasses.field(default_factory=list)
    remote_addr: str = dataclasses.field(default_factory=str)


def test_good_solve_user_mode():
    """
    Test that a user can solve a challenge in user mode.
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        assert Solves.query.count() == 0
        solve_request = FakeRequest(form={"submission": "flag"})

        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1

        solve = Solves.query.filter_by(
            user_id=user.id, team_id=None, challenge_id=challenge.id
        ).first()
        assert solve is not None

    destroy_ctfd(app)


def test_good_solve_team_mode():
    """
    Test that a user can solve a challenge in team mode.
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Solves.query.count() == 0
        solve_request = FakeRequest(form={"submission": "flag"})

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        team = gen_team(app.db)

        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1

        solve = Solves.query.filter_by(
            user_id=user.id, team_id=team.id, challenge_id=challenge.id
        ).first()
        assert solve is not None


def test_duplicate_solve_user_mode():
    """
    Test that duplicate solves in user mode are not added to the database and don't raise an error.
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        assert Solves.query.count() == 0
        solve_request = FakeRequest(form={"submission": "flag"})

        # First solve attempt
        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1

        solve = Solves.query.filter_by(
            user_id=user.id, team_id=None, challenge_id=challenge.id
        ).first()
        assert solve is not None

        # Second solve attempt - should not be added to the database
        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1


def test_duplicate_solve_team_mode():
    """
    Test that duplicate solves in team mode are not added to the database and don't raise an error.
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        team = gen_team(app.db)

        assert Solves.query.count() == 0
        solve_request = FakeRequest(form={"submission": "flag"})

        # First solve attempt
        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1

        solve = Solves.query.filter_by(
            user_id=user.id, team_id=team.id, challenge_id=challenge.id
        ).first()
        assert solve is not None

        # Second solve attempt - should not be added to the database
        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1


def test_bad_submission():
    """
    Test that a malformed solve request does not add to Solves table
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        assert Solves.query.count() == 0

        bad_solve_request = FakeRequest(form={"submission": None})
        r = BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=bad_solve_request
        )
        assert r == (False, "No submission sent")
        assert Solves.query.count() == 0

        # Note: the solve() function does NOT validate the accuracy of flags!
        # Thus, we expect the following to be successful
        bad_solve_request = FakeRequest(form={"submission": "incorrect_flag"})
        r = BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=bad_solve_request
        )
        assert r is None
        assert Solves.query.count() == 1


def test_empty_solve_request():
    """
    Test that an empty solve request does not add a solve to the database.
    """
    app = create_ctfd(enable_plugins=True)
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Users.query.count() == 1
        user = Users.query.filter_by(id=1).first()

        assert Solves.query.count() == 0

        # No submission sent
        solve_request = FakeRequest(form={})

        with pytest.raises(
            Exception, match="'FakeRequest' object has no attribute 'get_json'"
        ):
            BaseChallenge.solve(
                user=user, team=None, challenge=challenge, request=solve_request
            )

        assert Solves.query.count() == 0

    destroy_ctfd(app)
