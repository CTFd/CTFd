#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataclasses

import pytest

from CTFd.models import Challenges, Flags, Solves, Users
from CTFd.plugins.challenges import BaseChallenge
from tests.helpers import create_ctfd, destroy_ctfd, gen_challenge, gen_flag, gen_team


@dataclasses.dataclass
class FakeRequest:
    form: dict[str, str]
    access_route: list[str] = dataclasses.field(default_factory=list)
    remote_addr: str = dataclasses.field(default_factory=str)


def test_good_user_mode_solve():
    """
    Test that good solve() in user mode (team=None) adds to the Solves table.
    """
    app = create_ctfd()
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


def test_good_team_mode_solve():
    """
    Test that good solve() in team mode (team=not None) adds to the Solves table in team mode.
    """
    app = create_ctfd()
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


def test_duplicate_user_mode_solve():
    """
    Test that duplicate solve() in user mode (team=None) does not add to Solves table twice, and does not raise an error.
    """
    app = create_ctfd()
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


def test_duplicate_team_mode_solve():
    """
    Test that duplicate solve() in team mode (team=not None) does not add to Solves table twice, and does not raise an error.
    """
    app = create_ctfd()
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


def test_bad_submission_solve():
    """
    Test that passing malformed request to solve() does not add to Solves table
    """
    app = create_ctfd()
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


def test_empty_request_solve():
    """
    Test that passing an empty request to solve() does not add to Solves table
    """
    app = create_ctfd()
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


def test_correct_attempt():
    """
    Test that passing a correct flag to attempt() returns (True, "Correct") and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        flag = gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1

        correct_attempt = FakeRequest(form={"submission": flag.content})
        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_incorrect_attempt():
    """
    Test that passing an incorrect flag to attempt() returns (False, "Incorrect") and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1

        incorrect_attempt = FakeRequest(form={"submission": "incorrect_flag"})
        r = BaseChallenge.attempt(challenge=challenge, request=incorrect_attempt)
        assert r == (False, "Incorrect")
        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_duplicate_attempt():
    """
    Test that passing a duplicate flag to attempt() returns (True, "Correct") and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        flag = gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1

        correct_attempt = FakeRequest(form={"submission": flag.content})
        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0

        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_bad_submission_attempt():
    """
    Test that passing a None submission to attempt() returns (False, "No submission sent") and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1

        bad_attempt = FakeRequest(form={"submission": None})
        r = BaseChallenge.attempt(challenge=challenge, request=bad_attempt)
        assert r == (False, "No submission sent")
        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_empty_form_attempt():
    """
    Test that passing a request with empty form to attempt() raises an exception and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)

        assert Challenges.query.count() == 1
        assert Flags.query.filter_by(challenge_id=challenge.id).count() == 1

        empty_attempt = FakeRequest(form={})
        with pytest.raises(
            Exception, match="'FakeRequest' object has no attribute 'get_json'"
        ):
            BaseChallenge.attempt(challenge=challenge, request=empty_attempt)
        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_empty_flag_attempt():
    """
    Test that passing an empty flag to attempt() returns (True, "Correct") when the flag matches the challenge's flag and does not add to the Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        flag = gen_flag(app.db, challenge.id, content="")

        assert flag.content == ""
        assert Challenges.query.count() == 1

        empty_flag_attempt = FakeRequest(form={"submission": ""})
        r = BaseChallenge.attempt(challenge=challenge, request=empty_flag_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0

    destroy_ctfd(app)
