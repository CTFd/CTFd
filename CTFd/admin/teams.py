from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Solves, Awards, Unlocks, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs
from CTFd.admin import admin
from CTFd.utils.helpers import get_errors, get_infos

from sqlalchemy.sql import not_


@admin.route('/admin/teams')
@admins_only
def teams_listing():
    page = abs(request.args.get('page', 1, type=int))
    q = request.args.get('q')
    if q:
        field = request.args.get('field')
        teams = []
        errors = get_errors()
        if field == 'id':
            if q.isnumeric():
                teams = Teams.query.filter(Teams.id == q).order_by(Teams.id.asc()).all()
            else:
                teams = []
                errors.append('Your ID search term is not numeric')
        elif field == 'name':
            teams = Teams.query.filter(Teams.name.like('%{}%'.format(q))).order_by(Teams.id.asc()).all()
        elif field == 'email':
            teams = Teams.query.filter(Teams.email.like('%{}%'.format(q))).order_by(Teams.id.asc()).all()
        elif field == 'affiliation':
            teams = Teams.query.filter(Teams.affiliation.like('%{}%'.format(q))).order_by(Teams.id.asc()).all()
        return render_template('admin/teams/teams.html', teams=teams, pages=None, curr_page=None, q=q, field=field)

    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    teams = Teams.query.order_by(Teams.id.asc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Teams.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('admin/teams/teams.html', teams=teams, pages=pages, curr_page=page)


@admin.route('/admin/teams/new')
@admins_only
def teams_new():
    return render_template('admin/teams/new.html')


@admin.route('/admin/teams/<int:team_id>')
@admins_only
def teams_detail(team_id):
    team = Teams.query.filter_by(id=team_id).first_or_404()

    # Get members
    members = team.members
    member_ids = [member.id for member in members]

    # Get Solves for all members
    solves = team.get_solves(admin=True)
    fails = team.get_fails(admin=True)
    awards = team.get_awards(admin=True)
    score = team.get_score(admin=True)
    place = team.get_place(admin=True)

    # Get missing Challenges for all members
    # TODO: How do you mark a missing challenge for a team?
    solve_ids = [s.challenge_id for s in solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()

    # Get addresses for all members
    last_seen = db.func.max(Tracking.date).label('last_seen')
    addrs = db.session.query(Tracking.ip, last_seen) \
                      .filter(Tracking.user_id.in_(member_ids)) \
                      .group_by(Tracking.ip) \
                      .order_by(last_seen.desc()).all()

    return render_template(
        'admin/teams/team.html',
        team=team,
        members=members,
        score=score,
        place=place,
        solves=solves,
        fails=fails,
        missing=missing,
        awards=awards,
        addrs=addrs,
    )
