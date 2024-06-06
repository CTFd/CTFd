#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataclasses

import pytest

from CTFd.models import Fails, Solves, Users
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
        user = Users.query.filter_by(id=1).first()
        solve_request = FakeRequest(form={"submission": "flag"})

        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        # There is only 1 new Solve
        assert Solves.query.count() == 1
        # That Solve is the one we just added
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_good_team_mode_solve():
    """
    Test that good solve() in team mode (team=not None) adds to the Solves table in team mode.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        team = gen_team(app.db)
        solve_request = FakeRequest(form={"submission": "flag"})

        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        # There is only 1 new Solve
        assert Solves.query.count() == 1
        # That Solve is the one we just added
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=team.id, challenge_id=challenge.id
            ).count()
            == 1
        )


def test_duplicate_user_mode_solve():
    """
    Test that duplicate solve() in user mode (team=None) does not add to Solves table twice,
    and does not raise an error.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        solve_request = FakeRequest(form={"submission": "flag"})

        # First solve attempt
        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

        # Second solve attempt - should not be added to the database
        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1


def test_duplicate_team_mode_solve():
    """
    Test that duplicate solve() in team mode (team=not None) does not add to Solves table twice,
    and does not raise an error.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        team = gen_team(app.db)
        solve_request = FakeRequest(form={"submission": "flag"})

        # First solve attempt
        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=team.id, challenge_id=challenge.id
            ).count()
            == 1
        )

        # Second solve attempt - should not be added to the database
        BaseChallenge.solve(
            user=user, team=team, challenge=challenge, request=solve_request
        )
        assert Solves.query.count() == 1


def test_incorrect_flag_solve():
    """
    Test that passing an incorrect flag to solve() does adds to Solves table because solve() does not
    validate the accuracy of flags. It should ONLY check if the submission is not empty and add to Solves table.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        # Note: the solve() function does NOT validate the accuracy of flags!
        # Thus, we expect the following to be successful
        incorrect_flag_request = FakeRequest(form={"submission": "incorrect_flag"})

        r = BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=incorrect_flag_request
        )
        assert r is None
        # There is only 1 new Solve
        assert Solves.query.count() == 1
        # That Solve is the one we just added
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_empty_flag_solve():
    """
    Test that passing an empty flag to solve() adds to Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        empty_flag_request = FakeRequest(form={"submission": ""})

        BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=empty_flag_request
        )
        # There is only 1 new Solve
        assert Solves.query.count() == 1
        # That Solve is the one we just added
        assert (
            Solves.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_none_submission_solve():
    """
    Test that passing malformed request to solve() does not add to Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        bad_solve_request = FakeRequest(form={"submission": None})

        r = BaseChallenge.solve(
            user=user, team=None, challenge=challenge, request=bad_solve_request
        )
        assert r == (False, "No submission sent")
        assert Solves.query.count() == 0


def test_empty_form_solve():
    """
    Test that passing an empty request to solve() does not add to Solves table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        solve_request = FakeRequest(form={})

        with pytest.raises(
            Exception, match="'FakeRequest' object has no attribute 'get_json'"
        ):
            BaseChallenge.solve(
                user=user, team=None, challenge=challenge, request=solve_request
            )

        assert Solves.query.count() == 0

    destroy_ctfd(app)


def test_correct_flag_attempt():
    """
    Test that passing a correct flag to attempt() returns (True, "Correct") and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        flag = gen_flag(app.db, challenge.id)
        correct_attempt = FakeRequest(form={"submission": flag.content})

        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_duplicate_correct_attempt():
    """
    Test that passing a duplicate flag to attempt() returns (True, "Correct") and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        flag = gen_flag(app.db, challenge.id)
        correct_attempt = FakeRequest(form={"submission": flag.content})

        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

        r = BaseChallenge.attempt(challenge=challenge, request=correct_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_incorrect_flag_attempt():
    """
    Test that passing an incorrect flag to attempt() returns (False, "Incorrect") and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)
        incorrect_attempt = FakeRequest(form={"submission": "incorrect_flag"})

        r = BaseChallenge.attempt(challenge=challenge, request=incorrect_attempt)
        assert r == (False, "Incorrect")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_duplicate_incorrect_attempt():
    """
    Test that passing a duplicate incorrect flag to attempt() returns (False, "Incorrect") and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)
        incorrect_attempt = FakeRequest(form={"submission": "incorrect_flag"})

        r = BaseChallenge.attempt(challenge=challenge, request=incorrect_attempt)
        assert r == (False, "Incorrect")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

        r = BaseChallenge.attempt(challenge=challenge, request=incorrect_attempt)
        assert r == (False, "Incorrect")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_empty_flag_attempt():
    """
    Test that passing an empty flag to attempt() returns (True, "Correct") when the flag matches
    the challenge's flag and does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id, content="")
        empty_flag_attempt = FakeRequest(form={"submission": ""})

        r = BaseChallenge.attempt(challenge=challenge, request=empty_flag_attempt)
        assert r == (True, "Correct")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_none_submission_attempt():
    """
    Test that passing a None submission to attempt() returns (False, "No submission sent") and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)
        bad_attempt = FakeRequest(form={"submission": None})

        r = BaseChallenge.attempt(challenge=challenge, request=bad_attempt)
        assert r == (False, "No submission sent")
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_empty_form_attempt():
    """
    Test that passing a request with empty form to attempt() raises an exception and
    does not add to the Solves or Fails tables
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        gen_flag(app.db, challenge.id)
        empty_attempt = FakeRequest(form={})

        with pytest.raises(
            Exception, match="'FakeRequest' object has no attribute 'get_json'"
        ):
            BaseChallenge.attempt(challenge=challenge, request=empty_attempt)
        assert Solves.query.count() == 0
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_good_user_mode_fail():
    """
    Test that good fail() in user mode (team=None) adds to the Fails table.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        fail_request = FakeRequest(form={"submission": "flag"})

        BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=fail_request
        )
        # There is only 1 new Fail
        assert Fails.query.count() == 1
        # That Fail is the one we just added
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_good_team_mode_fail():
    """
    Test that good fail() in team mode (team=not None) adds to the Fails table in team mode.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        team = gen_team(app.db)
        fail_request = FakeRequest(form={"submission": "flag"})

        BaseChallenge.fail(
            user=user, team=team, challenge=challenge, request=fail_request
        )
        # There is only 1 new Fail
        assert Fails.query.count() == 1
        # That Fail is the one we just added
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=team.id, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_duplicate_user_mode_fail():
    """
    Test that duplicate fail() in user mode (team=None) adds to Fails table twice,
    and does not raise an error.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        fail_request = FakeRequest(form={"submission": "flag"})

        # First fail attempt
        BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=fail_request
        )
        assert Fails.query.count() == 1
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

        # Second fail attempt - should not be added to the database
        BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=fail_request
        )
        assert Fails.query.count() == 2
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 2
        )

    destroy_ctfd(app)


def test_duplicate_team_mode_fail():
    """
    Test that duplicate fail() in team mode (team=not None) adds to Fails table twice,
    and does not raise an error.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        team = gen_team(app.db)
        fail_request = FakeRequest(form={"submission": "flag"})

        # First fail attempt
        BaseChallenge.fail(
            user=user, team=team, challenge=challenge, request=fail_request
        )
        assert Fails.query.count() == 1
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=team.id, challenge_id=challenge.id
            ).count()
            == 1
        )

        # Second fail attempt - should not be added to the database
        BaseChallenge.fail(
            user=user, team=team, challenge=challenge, request=fail_request
        )
        assert Fails.query.count() == 2
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=team.id, challenge_id=challenge.id
            ).count()
            == 2
        )

    destroy_ctfd(app)


def test_incorrect_flag_fail():
    """
    Test that passing an incorrect flag to fail() does adds to Fails table because fail() does not validate
    the accuracy of flags. It should ONLY check if the submission is not empty and add to Fails table.
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        # Note: the fail() function does NOT validate the accuracy of flags!
        # Thus, we expect the following to be successful
        bad_fail_request = FakeRequest(form={"submission": "incorrect_flag"})

        r = BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=bad_fail_request
        )
        assert r is None
        # There is only 1 new Fail
        assert Fails.query.count() == 1
        # That Fail is the one we just added
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_empty_flag_fail():
    """
    Test that passing an empty flag to fail() adds to Fails table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        empty_flag_request = FakeRequest(form={"submission": ""})

        BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=empty_flag_request
        )
        # There is only 1 new Fail
        assert Fails.query.count() == 1
        # That Fail is the one we just added
        assert (
            Fails.query.filter_by(
                user_id=user.id, team_id=None, challenge_id=challenge.id
            ).count()
            == 1
        )

    destroy_ctfd(app)


def test_none_submission_fail():
    """
    Test that passing malformed request to fail() does not add to Fails table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        bad_fail_request = FakeRequest(form={"submission": None})

        r = BaseChallenge.fail(
            user=user, team=None, challenge=challenge, request=bad_fail_request
        )
        assert r == (False, "No submission sent")
        assert Fails.query.count() == 0

    destroy_ctfd(app)


def test_empty_form_fail():
    """
    Test that passing an empty request to fail() does not add to Fails table
    """
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = Users.query.filter_by(id=1).first()
        fail_request = FakeRequest(form={})

        with pytest.raises(
            Exception, match="'FakeRequest' object has no attribute 'get_json'"
        ):
            BaseChallenge.fail(
                user=user, team=None, challenge=challenge, request=fail_request
            )

        assert Fails.query.count() == 0

    destroy_ctfd(app)
