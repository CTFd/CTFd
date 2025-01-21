import functools
from pathlib import Path
from CTFd.constants.config import ChallengeVisibilityTypes
from CTFd.models import Configs
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, view_after_ctf
from CTFd.utils import config, user as current_user
from CTFd.utils.decorators import require_complete_profile, require_verified_emails
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers import get_errors, get_infos
from CTFd.utils.plugins import override_template
from flask import render_template, url_for, redirect,request, abort


def during_ctf_time_only(f):
    """
    Decorator to restrict an endpoint to only be seen during a CTF
    :param f:
    :return:
    """

    @functools.wraps(f)
    def during_ctf_time_only_wrapper(*args, **kwargs):
        if ctftime() or current_user.is_admin():
            return f(*args, **kwargs)
        else:
            if ctf_ended():
                if view_after_ctf():
                    return f(*args, **kwargs)
                else:
                    error = "{} has ended".format(config.ctf_name())
                    abort(403, description=error)
            if ctf_started() is False:
                if config.is_teams_mode() and current_user.get_current_team() is None:
                    return redirect(url_for("teams.private", next=request.full_path))
                else:
                    error = "{} has not started yet".format(config.ctf_name())
                    abort(403, description=error)

    return during_ctf_time_only_wrapper

def registerTemplate(old_path, new_path):
        dir_path = Path(__file__).parent.resolve()
        template_path = dir_path/'templates'/new_path
        override_template(old_path,open(template_path).read())

def load(app):

    '''
        discarding for the moment because it doesn't work as I want it to 
    @require_complete_profile
    @during_ctf_time_only
    @require_verified_emails
    @check_challenge_visibility
    def ChallengeError():
        if (
            Configs.challenge_visibility == ChallengeVisibilityTypes.PUBLIC
            and current_user.authed() is False
        ):
            pass
        else:
            if config.is_teams_mode() and current_user.get_current_team() is None:
                return redirect(url_for("teams.private", next=request.full_path))

        infos = get_infos()
        errors = get_errors()

        if Configs.challenge_visibility == ChallengeVisibilityTypes.ADMINS:
            infos.append("Challenge Visibility is set to Admins Only")

        if ctf_started() is False:
            errors.append(f"{Configs.ctf_name} has not started yet")

        if ctf_paused() is True:
            infos.append(f"{Configs.ctf_name} is paused")

        if ctf_ended() is True:
            infos.append(f"{Configs.ctf_name} has ended")

        return render_template("challenges.html", infos=infos, errors=errors)
    '''

    # blanket replacing all error 403s to not have the error number displayed
    registerTemplate('errors/403.html','403Modified.html')