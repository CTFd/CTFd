import functools

from flask import abort, redirect, render_template, request, url_for

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.utils import get_config
from CTFd.utils.user import authed, is_admin


def check_score_visibility(f):
    @functools.wraps(f)
    def _check_score_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.SCORE_VISIBILITY)
        if v == ScoreVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == ScoreVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == ScoreVisibilityTypes.HIDDEN:
            return (
                render_template("errors/403.html", error="Scores are currently hidden"),
                403,
            )

        elif v == ScoreVisibilityTypes.ADMINS:
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_score_visibility


def check_challenge_visibility(f):
    @functools.wraps(f)
    def _check_challenge_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.CHALLENGE_VISIBILITY)
        if v == ChallengeVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == ChallengeVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == ChallengeVisibilityTypes.ADMINS:
            if is_admin():
                return f(*args, **kwargs)
            else:
                if authed():
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

    return _check_challenge_visibility


def check_account_visibility(f):
    @functools.wraps(f)
    def _check_account_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.ACCOUNT_VISIBILITY)
        if v == AccountVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == AccountVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == AccountVisibilityTypes.ADMINS:
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_account_visibility


def check_registration_visibility(f):
    @functools.wraps(f)
    def _check_registration_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.REGISTRATION_VISIBILITY)
        if v == RegistrationVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)
        elif v == RegistrationVisibilityTypes.PRIVATE:
            abort(404)

    return _check_registration_visibility
