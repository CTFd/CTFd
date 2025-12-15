#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from flask import request
from sqlalchemy.exc import IntegrityError

from CTFd.exceptions.challenges import ChallengeSolveException
from CTFd.models import Solves
from CTFd.plugins.challenges import BaseChallenge
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_solve,
    gen_team,
    gen_user,
)


def test_base_challenge_solve_creates_solve_when_missing():
    """Test that BaseChallenge.solve() creates a solve if it doesn't exist"""
    app = create_ctfd()
    with app.app_context():
        challenge = gen_challenge(app.db)
        user = gen_user(app.db, name="solver", email="solver@example.com")

        assert Solves.query.count() == 0

        with app.test_request_context(
            json={"submission": "flag"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            BaseChallenge.solve(user, None, challenge, request)

        assert Solves.query.count() == 1
    destroy_ctfd(app)


def test_base_challenge_solve_raises_on_duplicate_solve():
    """Test that BaseChallenge.solve() raises ChallengeSolveException on duplicate solve"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        challenge = gen_challenge(app.db)
        team = gen_team(app.db, member_count=1)
        user = team.members[0]

        gen_solve(app.db, user_id=user.id, team_id=team.id, challenge_id=challenge.id)
        assert Solves.query.count() == 1

        with app.test_request_context(
            json={"submission": "flag"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with pytest.raises(ChallengeSolveException) as exc:
                BaseChallenge.solve(user, team, challenge, request)

            assert isinstance(exc.value.__cause__, IntegrityError)

        assert Solves.query.count() == 1
    destroy_ctfd(app)
