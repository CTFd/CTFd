from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Solves, Awards, Unlocks, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/teams')
@admins_only
def admin_teams_view():
    page = request.args.get('page', 1)
    q = request.args.get('q')
    if q:
        field = request.args.get('field')
        teams = []
        errors = []
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
        elif field == 'country':
            teams = Teams.query.filter(Teams.country.like('%{}%'.format(q))).order_by(Teams.id.asc()).all()
        return render_template('admin/teams.html', teams=teams, pages=None, curr_page=None, q=q, field=field)

    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    teams = Teams.query.order_by(Teams.id.asc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Teams.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('admin/teams.html', teams=teams, pages=pages, curr_page=page)


# @admin.route('/admin/team/new', methods=['POST'])
# @admins_only
# def admin_create_team():
#     # TODO: Move to API
#     name = request.form.get('name', None)
#     password = request.form.get('password', None)
#     email = request.form.get('email', None)
#     website = request.form.get('website', None)
#     affiliation = request.form.get('affiliation', None)
#     country = request.form.get('country', None)
#
#     admin_user = True if request.form.get('admin', None) == 'on' else False
#     verified = True if request.form.get('verified', None) == 'on' else False
#     hidden = True if request.form.get('hidden', None) == 'on' else False
#
#     errors = []
#
#     if not name:
#         errors.append('The team requires a name')
#     elif Teams.query.filter(Teams.name == name).first():
#         errors.append('That name is taken')
#
#     if utils.check_email_format(name) is True:
#         errors.append('Team name cannot be an email address')
#
#     if not email:
#         errors.append('The team requires an email')
#     elif Teams.query.filter(Teams.email == email).first():
#         errors.append('That email is taken')
#
#     if email:
#         valid_email = utils.check_email_format(email)
#         if not valid_email:
#             errors.append("That email address is invalid")
#
#     if not password:
#         errors.append('The team requires a password')
#
#     if website and (website.startswith('http://') or website.startswith('https://')) is False:
#         errors.append('Websites must start with http:// or https://')
#
#     if errors:
#         db.session.close()
#         return jsonify({'data': errors})
#
#     team = Teams(name, email, password)
#     team.website = website
#     team.affiliation = affiliation
#     team.country = country
#
#     team.admin = admin_user
#     team.verified = verified
#     team.hidden = hidden
#
#     db.session.add(team)
#     db.session.commit()
#     db.session.close()
#     return jsonify({'data': ['success']})


@admin.route('/admin/teams/<int:team_id>')
@admins_only
def admin_team(team_id):
    team = Teams.query.filter_by(id=team_id).first_or_404()

    # Get members
    members = team.members

    member_ids = [member.id for member in members]

    # Get Solves for all members
    solves = Solves.query.filter(
        Solves.user_id.in_(member_ids)
    ).all()

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

    # Get Fails for every member
    fails = Fails.query.filter(
        Fails.user_id.in_(member_ids)
    ).order_by(
        Fails.date.asc()
    ).all()

    awards = Awards.query.filter(
        Awards.user_id.in_(member_ids)
    ).order_by(Awards.date.asc()).all()

    score = team.get_score(admin=True)
    place = team.get_place(admin=True)

    return render_template(
        'admin/team.html',
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


# TODO: Teams won't be emailed on first release
# @admin.route('/admin/team/<int:teamid>/mail', methods=['POST'])
# @admins_only
# @ratelimit(method="POST", limit=10, interval=60)
# def email_user(teamid):
#     # TODO: Not sure where to move this.
#     msg = request.form.get('msg', None)
#     team = Teams.query.filter(Teams.id == teamid).first_or_404()
#     if msg and team:
#         result, response = utils.sendmail(team.email, msg)
#         return jsonify({
#             'result': result,
#             'message': response
#         })
#     else:
#         return jsonify({
#             'result': False,
#             'message': "Missing information"
#         })


@admin.route('/admin/solves/<int:teamid>/<int:chalid>/solve', methods=['POST'])
@admins_only
def create_solve(teamid, chalid):
    # TODO: Move to API. Not sure where.
    solve = Solves(teamid=teamid, chalid=chalid, ip='127.0.0.1', flag='MARKED_AS_SOLVED_BY_ADMIN')
    db.session.add(solve)
    db.session.commit()
    db.session.close()
    return '1'
