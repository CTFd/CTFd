from flask import request, redirect, url_for, session, abort
from CTFd import utils
import functools


def during_ctf_time_only(f):
    """
    Decorator to restrict an endpoint to only be seen during a CTF
    :param f:
    :return:
    """
    @functools.wraps(f)
    def during_ctf_time_only_wrapper(*args, **kwargs):
        if utils.ctftime() or utils.is_admin():
            return f(*args, **kwargs)
        else:
            if utils.ctf_ended():
                if utils.view_after_ctf():
                    return f(*args, **kwargs)
                else:
                    error = '{} has ended'.format(utils.ctf_name())
                    abort(403, description=error)

            if utils.ctf_started() is False:
                error = '{} has not started yet'.format(utils.ctf_name())
                abort(403, description=error)
    return during_ctf_time_only_wrapper


def require_verified_emails(f):
    """
    Decorator to restrict an endpoint to users with confirmed active email addresses
    :param f:
    :return:
    """
    @functools.wraps(f)
    def require_verified_emails_wrapper(*args, **kwargs):
        if utils.get_config('verify_emails'):
            if utils.authed():
                if utils.is_admin() is False and utils.is_verified() is False:  # User is not confirmed
                    return redirect(url_for('auth.confirm_user'))
        return f(*args, **kwargs)
    return require_verified_emails_wrapper


def viewable_without_authentication(status_code=None):
    """
    Decorator that allows users to view the specified endpoint if viewing challenges without authentication is enabled
    :param status_code:
    :return:
    """
    def viewable_without_authentication_decorator(f):
        @functools.wraps(f)
        def viewable_without_authentication_wrapper(*args, **kwargs):
            if utils.user_can_view_challenges():
                return f(*args, **kwargs)
            else:
                if status_code:
                    if status_code == 403:
                        error = "An authorization error has occured"
                    abort(status_code, description=error)
                return redirect(url_for('auth.login', next=request.path))
        return viewable_without_authentication_wrapper
    return viewable_without_authentication_decorator


def authed_only(f):
    """
    Decorator that requires the user to be authenticated
    :param f:
    :return:
    """
    @functools.wraps(f)
    def authed_only_wrapper(*args, **kwargs):
        if session.get('id'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.login', next=request.path))

    return authed_only_wrapper


def admins_only(f):
    """
    Decorator that requires the user to be authenticated and an admin
    :param f:
    :return:
    """
    @functools.wraps(f)
    def admins_only_wrapper(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.login', next=request.path))

    return admins_only_wrapper
