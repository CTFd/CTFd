from flask import request, abort, redirect, url_for, render_template
from CTFd.utils import get_config
from CTFd.utils.user import is_admin, authed
import functools


def check_score_visibility(f):
    @functools.wraps(f)
    def _check_score_visibility(*args, **kwargs):
        v = get_config("score_visibility")
        if v == "public":
            return f(*args, **kwargs)

        elif v == "private":
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == "hidden":
            return (
                render_template("errors/403.html", error="Scores are currently hidden"),
                403,
            )

        elif v == "admins":
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_score_visibility


def check_challenge_visibility(f):
    @functools.wraps(f)
    def _check_challenge_visibility(*args, **kwargs):
        v = get_config("challenge_visibility")
        if v == "public":
            return f(*args, **kwargs)

        elif v == "private":
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == "admins":
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
        v = get_config("account_visibility")
        if v == "public":
            return f(*args, **kwargs)

        elif v == "private":
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == "admins":
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_account_visibility


def check_registration_visibility(f):
    @functools.wraps(f)
    def _check_registration_visibility(*args, **kwargs):
        v = get_config("registration_visibility")
        if v == "public":
            return f(*args, **kwargs)
        elif v == "private":
            abort(404)

    return _check_registration_visibility
