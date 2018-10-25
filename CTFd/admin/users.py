from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Users, Solves, Fails, Challenges, Tracking, Awards
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/users')
@admins_only
def user_list():
    page = request.args.get('page', 1)

    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    users = Users.query.order_by(Users.id.asc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Users.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)

    return render_template('admin/users/users.html', users=users, pages=pages, curr_page=page)


@admin.route('/admin/users/new')
@admins_only
def user_new():
    return render_template('admin/users/new.html')


@admin.route('/admin/users/<int:user_id>')
@admins_only
def user_detail(user_id):
    # Get user object
    user = Users.query.filter_by(id=user_id).first_or_404()

    # Get the user's solves
    solves = Solves.query.filter_by(user_id=user_id).all()

    # Get challenges that the user is missing
    solve_ids = [s.challenge_id for s in solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()

    # Get IP addresses that the User has used
    last_seen = db.func.max(Tracking.date).label('last_seen')
    addrs = db.session.query(Tracking.ip, last_seen) \
        .filter_by(user_id=user_id) \
        .group_by(Tracking.ip) \
        .order_by(last_seen.desc()).all()

    # Get Fails
    fails = Fails.query.filter_by(user_id=user_id).order_by(Fails.date.asc()).all()

    # Get Awards
    awards = Awards.query.filter_by(user_id=user_id).order_by(Awards.date.asc()).all()

    # Get user properties
    score = user.get_score(admin=True)
    place = user.get_place(admin=True)

    return render_template(
        'admin/users/user.html',
        solves=solves,
        user=user,
        addrs=addrs,
        score=score,
        missing=missing,
        place=place,
        fails=fails,
        awards=awards
    )