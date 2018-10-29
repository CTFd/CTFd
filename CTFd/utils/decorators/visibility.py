from CTFd.utils import config, get_config
from CTFd.utils.user import is_admin, authed
from flask import request, abort, redirect, url_for
import functools


def check_score_visibility(f):
    @functools.wraps(f)
    def _check_score_visibility(*args, **kwargs):
        v = get_config('score_visibility')
        if v == 'public':
            return f(*args, **kwargs)

        elif v == 'private':
            if authed():
                return f(*args, **kwargs)
            else:
                return redirect(url_for('auth.login', next=request.path))

        elif v == 'admins':
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)
    return _check_score_visibility


def check_challenge_visibility(f):
    @functools.wraps(f)
    def _check_challenge_visibility(*args, **kwargs):
        v = get_config('challenge_visibility')
        if v == 'public':
            return f(*args, **kwargs)

        elif v == 'private':
            if authed():
                return f(*args, **kwargs)
            else:
                return redirect(url_for('auth.login', next=request.path))
    return _check_challenge_visibility


def check_account_visibility(f):
    @functools.wraps(f)
    def _check_account_visibility(*args, **kwargs):
        v = get_config('account_visibility')
        if v == 'public':
            return f(*args, **kwargs)
        elif v == 'private':
            if authed():
                return f(*args, **kwargs)
            else:
                return redirect(url_for('auth.login', next=request.path))
        elif v == 'admins':
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)
    return _check_account_visibility


def check_registration_visibility(f):
    @functools.wraps(f)
    def _check_registration_visibility(*args, **kwargs):
        v = get_config('registration_visibility')
        if v == 'public':
            return f(*args, **kwargs)
        elif v == 'private':
            abort(404)
    return _check_registration_visibility
