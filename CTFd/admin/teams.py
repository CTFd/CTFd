from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache
from CTFd.models import db, Teams, Solves, Awards, Unlocks, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils

admin_teams = Blueprint('admin_teams', __name__)

@admin_teams.route('/admin/teams', defaults={'page': '1'})
@admin_teams.route('/admin/teams/<int:page>')
@admins_only
def admin_teams_view(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    teams = Teams.query.order_by(Teams.id.asc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Teams.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('admin/teams.html', teams=teams, pages=pages, curr_page=page)


@admin_teams.route('/admin/team/<int:teamid>', methods=['GET', 'POST'])
@admins_only
def admin_team(teamid):
    user = Teams.query.filter_by(id=teamid).first_or_404()

    if request.method == 'GET':
        solves = Solves.query.filter_by(teamid=teamid).all()
        solve_ids = [s.chalid for s in solves]
        missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()
        last_seen = db.func.max(Tracking.date).label('last_seen')
        addrs = db.session.query(Tracking.ip, last_seen) \
                          .filter_by(team=teamid) \
                          .group_by(Tracking.ip) \
                          .order_by(last_seen.desc()).all()
        wrong_keys = WrongKeys.query.filter_by(teamid=teamid).order_by(WrongKeys.date.asc()).all()
        awards = Awards.query.filter_by(teamid=teamid).order_by(Awards.date.asc()).all()
        score = user.score(admin=True)
        place = user.place(admin=True)
        return render_template('admin/team.html', solves=solves, team=user, addrs=addrs, score=score, missing=missing,
                               place=place, wrong_keys=wrong_keys, awards=awards)
    elif request.method == 'POST':
        admin_user = request.form.get('admin', None)
        if admin_user:
            admin_user = True if admin_user == 'true' else False
            user.admin = admin_user
            # Set user.banned to hide admins from scoreboard
            user.banned = admin_user
            db.session.commit()
            db.session.close()
            return jsonify({'data': ['success']})

        verified = request.form.get('verified', None)
        if verified:
            verified = True if verified == 'true' else False
            user.verified = verified
            db.session.commit()
            db.session.close()
            return jsonify({'data': ['success']})

        name = request.form.get('name', None)
        password = request.form.get('password', None)
        email = request.form.get('email', None)
        website = request.form.get('website', None)
        affiliation = request.form.get('affiliation', None)
        country = request.form.get('country', None)

        errors = []

        name_used = Teams.query.filter(Teams.name == name).first()
        if name_used and int(name_used.id) != int(teamid):
            errors.append('That name is taken')

        email_used = Teams.query.filter(Teams.email == email).first()
        if email_used and int(email_used.id) != int(teamid):
            errors.append('That email is taken')

        if errors:
            db.session.close()
            return jsonify({'data': errors})
        else:
            user.name = name
            if email:
                user.email = email
            if password:
                user.password = bcrypt_sha256.encrypt(password)
            user.website = website
            user.affiliation = affiliation
            user.country = country
            db.session.commit()
            db.session.close()
            return jsonify({'data': ['success']})


@admin_teams.route('/admin/team/<int:teamid>/mail', methods=['POST'])
@admins_only
def email_user(teamid):
    message = request.form.get('msg', None)
    team = Teams.query.filter(Teams.id == teamid).first()
    if message and team:
        if utils.sendmail(team.email, message):
            return '1'
    return '0'


@admin_teams.route('/admin/team/<int:teamid>/ban', methods=['POST'])
@admins_only
def ban(teamid):
    user = Teams.query.filter_by(id=teamid).first_or_404()
    user.banned = True
    db.session.commit()
    db.session.close()
    return redirect(url_for('admin_scoreboard.admin_scoreboard_view'))


@admin_teams.route('/admin/team/<int:teamid>/unban', methods=['POST'])
@admins_only
def unban(teamid):
    user = Teams.query.filter_by(id=teamid).first_or_404()
    user.banned = False
    db.session.commit()
    db.session.close()
    return redirect(url_for('admin_scoreboard.admin_scoreboard_view'))


@admin_teams.route('/admin/team/<int:teamid>/delete', methods=['POST'])
@admins_only
def delete_team(teamid):
    try:
        Unlocks.query.filter_by(teamid=teamid).delete()
        Awards.query.filter_by(teamid=teamid).delete()
        WrongKeys.query.filter_by(teamid=teamid).delete()
        Solves.query.filter_by(teamid=teamid).delete()
        Tracking.query.filter_by(team=teamid).delete()
        Teams.query.filter_by(id=teamid).delete()
        db.session.commit()
        db.session.close()
    except DatabaseError:
        return '0'
    else:
        return '1'


@admin_teams.route('/admin/solves/<teamid>', methods=['GET'])
@admins_only
def admin_solves(teamid="all"):
    if teamid == "all":
        solves = Solves.query.all()
    else:
        solves = Solves.query.filter_by(teamid=teamid).all()
        awards = Awards.query.filter_by(teamid=teamid).all()
    db.session.close()
    json_data = {'solves': []}
    for x in solves:
        json_data['solves'].append({
            'id': x.id,
            'chal': x.chal.name,
            'chalid': x.chalid,
            'team': x.teamid,
            'value': x.chal.value,
            'category': x.chal.category,
            'time': utils.unix_time(x.date)
        })
    for award in awards:
        json_data['solves'].append({
            'chal': award.name,
            'chalid': None,
            'team': award.teamid,
            'value': award.value,
            'category': award.category or "Award",
            'time': utils.unix_time(award.date)
        })
    json_data['solves'].sort(key=lambda k: k['time'])
    return jsonify(json_data)


@admin_teams.route('/admin/fails/all', defaults={'teamid': 'all'}, methods=['GET'])
@admin_teams.route('/admin/fails/<int:teamid>', methods=['GET'])
@admins_only
def admin_fails(teamid):
    if teamid == "all":
        fails = WrongKeys.query.join(Teams, WrongKeys.teamid == Teams.id).filter(Teams.banned == False).count()
        solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False).count()
        db.session.close()
        json_data = {'fails': str(fails), 'solves': str(solves)}
        return jsonify(json_data)
    else:
        fails = WrongKeys.query.filter_by(teamid=teamid).count()
        solves = Solves.query.filter_by(teamid=teamid).count()
        db.session.close()
        json_data = {'fails': str(fails), 'solves': str(solves)}
        return jsonify(json_data)


@admin_teams.route('/admin/solves/<int:teamid>/<int:chalid>/solve', methods=['POST'])
@admins_only
def create_solve(teamid, chalid):
    solve = Solves(chalid=chalid, teamid=teamid, ip='127.0.0.1', flag='MARKED_AS_SOLVED_BY_ADMIN')
    db.session.add(solve)
    db.session.commit()
    db.session.close()
    return '1'


@admin_teams.route('/admin/solves/<int:keyid>/delete', methods=['POST'])
@admins_only
def delete_solve(keyid):
    solve = Solves.query.filter_by(id=keyid).first_or_404()
    db.session.delete(solve)
    db.session.commit()
    db.session.close()
    return '1'


@admin_teams.route('/admin/wrong_keys/<int:keyid>/delete', methods=['POST'])
@admins_only
def delete_wrong_key(keyid):
    wrong_key = WrongKeys.query.filter_by(id=keyid).first_or_404()
    db.session.delete(wrong_key)
    db.session.commit()
    db.session.close()
    return '1'

@admin_teams.route('/admin/awards/<int:award_id>/delete', methods=['POST'])
@admins_only
def delete_award(award_id):
    award = Awards.query.filter_by(id=award_id).first_or_404()
    db.session.delete(award)
    db.session.commit()
    db.session.close()
    return '1'

@admin_teams.route('/admin/teams/<int:teamid>/awards', methods=['GET'])
@admins_only
def admin_awards(teamid):
    awards = Awards.query.filter_by(teamid=teamid).all()

    awards_list = []
    for award in awards:
        awards_list.append({
            'id': award.id,
            'name': award.name,
            'description': award.description,
            'date': award.date,
            'value': award.value,
            'category': award.category,
            'icon': award.icon
        })
    json_data = {'awards': awards_list}
    return jsonify(json_data)


@admin_teams.route('/admin/awards/add', methods=['POST'])
@admins_only
def create_award():
    try:
        teamid = request.form['teamid']
        name = request.form.get('name', 'Award')
        value = request.form.get('value', 0)
        award = Awards(teamid, name, value)
        award.description = request.form.get('description')
        award.category = request.form.get('category')
        db.session.add(award)
        db.session.commit()
        db.session.close()
        return '1'
    except Exception as e:
        print(e)
        return '0'