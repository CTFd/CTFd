from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Solves, Awards, Unlocks, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, \
    Config
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/users', defaults={'page': '1'})
@admins_only
def list(page):
    page = request.args.get('page', 1)
    return render_template('admin/users.html')