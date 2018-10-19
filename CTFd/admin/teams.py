from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Solves, Awards, Unlocks, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/teams', defaults={'page': '1'})
@admin.route('/admin/teams/<int:page>')
@admins_only
def admin_teams_view(page):
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


@admin.route('/admin/teams/<int:teamid>')
@admins_only
def admin_team(teamid):
    # TODO: This doesn't work
    user = Teams.query.filter_by(id=teamid).first_or_404()

    solves = Solves.query.filter_by(teamid=teamid).all()
    solve_ids = [s.chalid for s in solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()
    last_seen = db.func.max(Tracking.date).label('last_seen')
    addrs = db.session.query(Tracking.ip, last_seen) \
                      .filter_by(team=teamid) \
                      .group_by(Tracking.ip) \
                      .order_by(last_seen.desc()).all()
    wrong_keys = Fails.query.filter_by(teamid=teamid).order_by(Fails.date.asc()).all()
    awards = Awards.query.filter_by(teamid=teamid).order_by(Awards.date.asc()).all()
    score = user.score(admin=True)
    place = user.place(admin=True)
    return render_template(
        'admin/team.html',
        solves=solves,
        team=user,
        addrs=addrs,
        score=score,
        missing=missing,
        place=place,
        wrong_keys=wrong_keys,
        awards=awards
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

#
# @admin.route('/admin/team/<int:teamid>/ban', methods=['POST'])
# @admins_only
# def ban(teamid):
#     # TODO: Move to API via Team PATCH method
#     user = Teams.query.filter_by(id=teamid).first_or_404()
#     user.banned = True
#     db.session.commit()
#     db.session.close()
#     return redirect(url_for('admin.admin_scoreboard_view'))
#
#
# @admin.route('/admin/team/<int:teamid>/unban', methods=['POST'])
# @admins_only
# def unban(teamid):
#     # TODO: Move to API via Team PATCH method
#     user = Teams.query.filter_by(id=teamid).first_or_404()
#     user.banned = False
#     db.session.commit()
#     db.session.close()
#     return redirect(url_for('admin.admin_scoreboard_view'))


@admin.route('/admin/solves/<int:teamid>/<int:chalid>/solve', methods=['POST'])
@admins_only
def create_solve(teamid, chalid):
    # TODO: Move to API. Not sure where.
    solve = Solves(teamid=teamid, chalid=chalid, ip='127.0.0.1', flag='MARKED_AS_SOLVED_BY_ADMIN')
    db.session.add(solve)
    db.session.commit()
    db.session.close()
    return '1'
