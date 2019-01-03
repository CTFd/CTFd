from flask import render_template, request
from CTFd.utils import get_config
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.utils.modes import USERS_MODE, TEAMS_MODE
from CTFd.models import db, Users, Challenges, Tracking
from CTFd.admin import admin
from CTFd.utils.helpers import get_errors, get_infos

from sqlalchemy.sql import not_


@admin.route('/admin/users')
@admins_only
def users_listing():
    page = abs(request.args.get('page', 1, type=int))
    q = request.args.get('q')
    if q:
        field = request.args.get('field')
        users = []
        errors = get_errors()
        if field == 'id':
            if q.isnumeric():
                users = Users.query.filter(Users.id == q).order_by(Users.id.asc()).all()
            else:
                users = []
                errors.append('Your ID search term is not numeric')
        elif field == 'name':
            users = Users.query.filter(Users.name.like('%{}%'.format(q))).order_by(Users.id.asc()).all()
        elif field == 'email':
            users = Users.query.filter(Users.email.like('%{}%'.format(q))).order_by(Users.id.asc()).all()
        elif field == 'affiliation':
            users = Users.query.filter(Users.affiliation.like('%{}%'.format(q))).order_by(Users.id.asc()).all()
        return render_template('admin/users/users.html', users=users, pages=None, curr_page=None, q=q, field=field)

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
def users_new():
    return render_template('admin/users/new.html')


@admin.route('/admin/users/<int:user_id>')
@admins_only
def users_detail(user_id):
    # Get user object
    user = Users.query.filter_by(id=user_id).first_or_404()

    # Get the user's solves
    solves = user.get_solves(admin=True)

    # Get challenges that the user is missing
    if get_config('user_mode') == TEAMS_MODE:
        if user.team:
            all_solves = user.team.get_solves(admin=True)
        else:
            all_solves = user.get_solves(admin=True)
    else:
        all_solves = user.get_solves(admin=True)

    solve_ids = [s.challenge_id for s in all_solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()

    # Get IP addresses that the User has used
    last_seen = db.func.max(Tracking.date).label('last_seen')
    addrs = db.session.query(Tracking.ip, last_seen) \
        .filter_by(user_id=user_id) \
        .group_by(Tracking.ip) \
        .order_by(last_seen.desc()).all()

    # Get Fails
    fails = user.get_fails(admin=True)

    # Get Awards
    awards = user.get_awards(admin=True)

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
