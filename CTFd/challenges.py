from flask import render_template, request, redirect, jsonify, url_for, session, Blueprint, abort
from CTFd.models import db, Challenges, Files, Solves, Fails, Flags, Tags, Teams, Awards, Hints, Unlocks
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    ratelimit,
    require_team
)
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils import config, text_type, user as current_user, get_config
from CTFd.utils.dates import ctftime, ctf_started, ctf_paused, ctf_ended, unix_time, unix_time_to_utc

challenges = Blueprint('challenges', __name__)


@challenges.route('/challenges', methods=['GET'])
@during_ctf_time_only
@require_verified_emails
@check_challenge_visibility
@require_team
def listing():
    infos = []
    errors = []
    start = get_config('start') or 0
    end = get_config('end') or 0

    if ctf_paused():
        infos.append('{} is paused'.format(config.ctf_name()))

    if not ctftime():
        if ctf_started() is False:
            errors.append('{} has not started yet'.format(config.ctf_name()))
        if ctf_ended():
            errors.append('{} has ended'.format(config.ctf_name()))
        return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))

    return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))
