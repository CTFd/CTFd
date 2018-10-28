from flask import current_app as app, render_template, request, redirect, abort, jsonify, url_for, session, Blueprint, \
    Response, send_file
from flask.helpers import safe_join
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Users, Teams, Solves, Awards, Files, Pages, Tracking
from CTFd.utils import markdown
from CTFd.caching import cache
from CTFd.utils import get_config, set_config
from CTFd.utils.user import authed, get_ip
from CTFd.utils.decorators import authed_only
from CTFd.utils import config
from CTFd.utils.config.pages import get_page
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import user as current_user
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, unix_time_to_utc
from CTFd.utils import validators

import os

users = Blueprint('users', __name__)


@users.route('/users')
def listing():
    # TODO: Implement this logic to either mimic the teams page or to only be visible when the ctf is in user only mode
    users = Users.query.all()
    return render_template(
        'users/users.html',
        users=users
    )


@users.route('/profile')
@users.route('/user')
@authed_only
def private():
    user_id = session['id']

    freeze = get_config('freeze')
    user = Users.query.filter_by(id=user_id).first_or_404()
    solves = Solves.query.filter_by(user_id=user_id)
    awards = Awards.query.filter_by(user_id=user_id)

    place = user.place
    score = user.score

    if freeze:
        freeze = unix_time_to_utc(freeze)
        if user_id != session.get('id'):
            solves = solves.filter(Solves.date < freeze)
            awards = awards.filter(Awards.date < freeze)

    solves = solves.all()
    awards = awards.all()

    return render_template(
        'users/user.html',
        solves=solves,
        awards=awards,
        user=user,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen()
    )


@users.route('/users/<int:user_id>')
def public(user_id):
    # TODO: This should be visible if user's login as themselves (user+team login, or user only login)
    user = Users.query.filter_by(id=user_id).first_or_404()
    return render_template('users/user.html', user=user)
