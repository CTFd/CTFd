from flask import current_app as app, render_template, request, redirect, abort, jsonify, url_for, session, Blueprint, \
    Response, send_file
from flask.helpers import safe_join
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Users, Teams, Solves, Awards, Files, Pages, Tracking
from CTFd.utils import cache, markdown
from CTFd.utils import get_config, set_config
from CTFd.utils.user import authed, get_ip
from CTFd.utils import config
from CTFd.utils.config.pages import get_page
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import user as current_user
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, unix_time_to_utc
from CTFd.utils import validators

import os

users = Blueprint('users', __name__)

@users.route('/users')
def listing(page):
    pass


@users.route('/user')
def private_page():
    pass


@users.route('/user/<int:user_id>')
def public_page(user_id):
    pass