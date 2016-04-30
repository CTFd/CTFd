from flask import render_template, request, redirect, abort, jsonify, url_for, session, Blueprint
from CTFd.utils import sha512, is_safe_url, authed, admins_only, is_admin, unix_time, unix_time_millis, get_config, set_config, sendmail, rmdir
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError
from itsdangerous import TimedSerializer, BadTimeSignature
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import union_all
from werkzeug.utils import secure_filename
from socket import inet_aton, inet_ntoa
from passlib.hash import bcrypt_sha256
from flask import current_app as app

import logging
import hashlib
import time
import re
import os
import json
import datetime
import calendar

admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
def admin_view():
    if is_admin():
        return redirect(url_for('admin.admin_graphs'))

    return redirect(url_for('auth.login'))


@admin.route('/admin/graphs')
@admins_only
def admin_graphs():
    return render_template('admin/graphs.html')


@admin.route('/admin/config', methods=['GET', 'POST'])
@admins_only
def admin_config():
    if request.method == "POST":
        start = None
        end = None
        if request.form.get('start'):
            start = int(request.form['start'])
        if request.form.get('end'):
            end = int(request.form['end'])
            if end < unix_time(datetime.datetime.now()):
                end = None

        try:
            view_challenges_unregistered = bool(request.form.get('view_challenges_unregistered', None))
            view_scoreboard_if_authed = bool(request.form.get('view_scoreboard_if_authed', None))
            prevent_registration = bool(request.form.get('prevent_registration', None))
            prevent_name_change = bool(request.form.get('prevent_name_change', None))
            view_after_ctf = bool(request.form.get('view_after_ctf', None))
            verify_emails = bool(request.form.get('verify_emails', None))
            mail_tls = bool(request.form.get('mail_tls', None))
            mail_ssl = bool(request.form.get('mail_ssl', None))
        except (ValueError, TypeError):
            view_challenges_unregistered = None
            view_scoreboard_if_authed = None
            prevent_registration = None
            prevent_name_change = None
            view_after_ctf = None
            verify_emails = None
            mail_tls = None
            mail_ssl = None
        finally:
            view_challenges_unregistered = set_config('view_challenges_unregistered', view_challenges_unregistered)
            view_scoreboard_if_authed = set_config('view_scoreboard_if_authed', view_scoreboard_if_authed)
            prevent_registration = set_config('prevent_registration', prevent_registration)
            prevent_name_change = set_config('prevent_name_change', prevent_name_change)
            view_after_ctf = set_config('view_after_ctf', view_after_ctf)
            verify_emails = set_config('verify_emails', verify_emails)
            mail_tls = set_config('mail_tls', mail_tls)
            mail_ssl = set_config('mail_ssl', mail_ssl)

        mail_server = set_config("mail_server", request.form.get('mail_server', None))
        mail_port = set_config("mail_port", request.form.get('mail_port', None))

        mail_username = set_config("mail_username", request.form.get('mail_username', None))
        mail_password = set_config("mail_password", request.form.get('mail_password', None))

        ctf_name = set_config("ctf_name", request.form.get('ctf_name', None))

        mg_base_url = set_config("mg_base_url", request.form.get('mg_base_url', None))
        mg_api_key = set_config("mg_api_key", request.form.get('mg_api_key', None))

        max_tries = set_config("max_tries", request.form.get('max_tries', None))

        db_start = Config.query.filter_by(key='start').first()
        db_start.value = start

        db_end = Config.query.filter_by(key='end').first()
        db_end.value = end

        db.session.add(db_start)
        db.session.add(db_end)

        db.session.commit()
        return redirect(url_for('admin.admin_config'))

    ctf_name = get_config('ctf_name')
    max_tries = get_config('max_tries')

    mail_server = get_config('mail_server')
    mail_port = get_config('mail_port')
    mail_username = get_config('mail_username')
    mail_password = get_config('mail_password')

    mg_api_key = get_config('mg_api_key')
    mg_base_url = get_config('mg_base_url')
    if not max_tries:
        set_config('max_tries', 0)
        max_tries = 0

    view_after_ctf = get_config('view_after_ctf')
    start = get_config('start')
    end = get_config('end')

    mail_tls = get_config('mail_tls')
    mail_ssl = get_config('mail_ssl')

    view_challenges_unregistered = get_config('view_challenges_unregistered')
    view_scoreboard_if_authed = get_config('view_scoreboard_if_authed')
    prevent_registration = get_config('prevent_registration')
    prevent_name_change = get_config('prevent_name_change')
    verify_emails = get_config('verify_emails')

    db.session.commit()
    db.session.close()

    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]

    curr_year = datetime.date.today().year
    start_days = 0
    end_days = 0

    if start:
        start = datetime.datetime.fromtimestamp(float(start))
        start_days = calendar.monthrange(start.year, start.month)[1]
    if end:
        end = datetime.datetime.fromtimestamp(float(end))
        end_days = calendar.monthrange(end.year, end.month)[1]

    return render_template('admin/config.html',
                           ctf_name=ctf_name,
                           start=start,
                           end=end,
                           max_tries=max_tries,
                           mail_server=mail_server,
                           mail_port=mail_port,
                           mail_username=mail_username,
                           mail_password=mail_password,
                           mail_tls=mail_tls,
                           mail_ssl=mail_ssl,
                           view_challenges_unregistered=view_challenges_unregistered,
                           view_scoreboard_if_authed=view_scoreboard_if_authed,
                           prevent_registration=prevent_registration,
                           mg_base_url=mg_base_url,
                           mg_api_key=mg_api_key,
                           prevent_name_change=prevent_name_change,
                           verify_emails=verify_emails,
                           view_after_ctf=view_after_ctf,
                           months=months,
                           curr_year=curr_year,
                           start_days=start_days,
                           end_days=end_days)


@admin.route('/admin/css', methods=['GET', 'POST'])
@admins_only
def admin_css():
    if request.method == 'POST':
        css = request.form['css']
        css = set_config('css', css)
        return "1"
    return "0"

@admin.route('/admin/pages', defaults={'route': None}, methods=['GET', 'POST'])
@admin.route('/admin/pages/<route>', methods=['GET', 'POST'])
@admins_only
def admin_pages(route):
    if request.method == 'GET' and request.args.get('mode') == 'create':
        return render_template('admin/editor.html')
    if route and request.method == 'GET':
        page = Pages.query.filter_by(route=route).first()
        return render_template('admin/editor.html', page=page)
    if route and request.method == 'POST':
        page = Pages.query.filter_by(route=route).first()
        errors = []
        html = request.form['html']
        route = request.form['route']
        if not route:
            errors.append('Missing URL route')
        if errors:
            page = Pages(html, "")
            return render_template('/admin/editor.html', page=page)
        if page:
            page.route = route
            page.html = html
            db.session.commit()
            return redirect(url_for('admin.admin_pages'))
        page = Pages(route, html)
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('admin.admin_pages'))
    pages = Pages.query.all()
    return render_template('admin/pages.html', routes=pages, css=get_config('css'))


@admin.route('/admin/page/<pageroute>/delete', methods=['POST'])
@admins_only
def delete_page(pageroute):
    page = Pages.query.filter_by(route=pageroute).first()
    db.session.delete(page)
    db.session.commit()
    return '1'


@admin.route('/admin/chals', methods=['POST', 'GET'])
@admins_only
def admin_chals():
    if request.method == 'POST':
        chals = Challenges.query.add_columns('id', 'name', 'value', 'description', 'category', 'hidden').order_by(Challenges.value).all()

        teams_with_points = db.session.query(Solves.teamid, Teams.name).join(Teams).filter(
            Teams.banned == None).group_by(
                Solves.teamid).count()

        json_data = {'game':[]}
        for x in chals:
            solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid==x[1], Teams.banned==None).count()
            if teams_with_points > 0:
                percentage = (float(solve_count) / float(teams_with_points))
            else:
                percentage = 0.0
            json_data['game'].append({
                'id': x.id,
                'name': x.name,
                'value': x.value,
                'description': x.description,
                'category': x.category,
                'hidden': x.hidden,
                'percentage_solved': percentage
            })

        db.session.close()
        return jsonify(json_data)
    else:
        return render_template('admin/chals.html')


@admin.route('/admin/keys/<chalid>', methods=['POST', 'GET'])
@admins_only
def admin_keys(chalid):
    if request.method == 'GET':
        chal = Challenges.query.filter_by(id=chalid).first_or_404()
        json_data = {'keys':[]}
        flags = json.loads(chal.flags)
        for i, x in enumerate(flags):
            json_data['keys'].append({'id':i, 'key':x['flag'], 'type':x['type']})
        return jsonify(json_data)
    elif request.method == 'POST':
        chal = Challenges.query.filter_by(id=chalid).first()

        newkeys = request.form.getlist('keys[]')
        newvals = request.form.getlist('vals[]')
        flags = []
        for flag, val in zip(newkeys, newvals):
            flag_dict = {'flag':flag, 'type':int(val)}
            flags.append(flag_dict)
        json_data = json.dumps(flags)

        chal.flags = json_data

        db.session.commit()
        db.session.close()
        return '1'


@admin.route('/admin/tags/<chalid>', methods=['GET', 'POST'])
@admins_only
def admin_tags(chalid):
    if request.method == 'GET':
        tags = Tags.query.filter_by(chal=chalid).all()
        json_data = {'tags':[]}
        for x in tags:
             json_data['tags'].append({'id':x.id, 'chal':x.chal, 'tag':x.tag})
        return jsonify(json_data)

    elif request.method == 'POST':
        newtags = request.form.getlist('tags[]')
        for x in newtags:
            tag = Tags(chalid, x)
            db.session.add(tag)
        db.session.commit()
        db.session.close()
        return '1'


@admin.route('/admin/tags/<tagid>/delete', methods=['POST'])
@admins_only
def admin_delete_tags(tagid):
    if request.method == 'POST':
        tag = Tags.query.filter_by(id=tagid).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()
        return "1"


@admin.route('/admin/files/<chalid>', methods=['GET', 'POST'])
@admins_only
def admin_files(chalid):
    if request.method == 'GET':
        files = Files.query.filter_by(chal=chalid).all()
        json_data = {'files':[]}
        for x in files:
            json_data['files'].append({'id':x.id, 'file':x.location})
        return jsonify(json_data)
    if request.method == 'POST':
        if request.form['method'] == "delete":
            f = Files.query.filter_by(id=request.form['file']).first_or_404()
            if os.path.exists(os.path.join(app.static_folder, 'uploads', f.location)): ## Some kind of os.path.isfile issue on Windows...
                os.unlink(os.path.join(app.static_folder, 'uploads', f.location))
            db.session.delete(f)
            db.session.commit()
            db.session.close()
            return "1"
        elif request.form['method'] == "upload":
            files = request.files.getlist('files[]')

            for f in files:
                filename = secure_filename(f.filename)

                if len(filename) <= 0:
                    continue

                md5hash = hashlib.md5(os.urandom(64)).hexdigest()

                if not os.path.exists(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash)):
                    os.makedirs(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash))

                f.save(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash, filename))
                db_f = Files(chalid, os.path.join('static', 'uploads', md5hash, filename))
                db.session.add(db_f)

            db.session.commit()
            db.session.close()
            return redirect(url_for('admin.admin_chals'))


@admin.route('/admin/teams', defaults={'page':'1'})
@admin.route('/admin/teams/<page>')
@admins_only
def admin_teams(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page

    teams = Teams.query.slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Teams.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('admin/teams.html', teams=teams, pages=pages, curr_page=page)


@admin.route('/admin/team/<teamid>', methods=['GET', 'POST'])
@admins_only
def admin_team(teamid):
    user = Teams.query.filter_by(id=teamid).first()

    if request.method == 'GET':
        solves = Solves.query.filter_by(teamid=teamid).all()
        solve_ids = [s.chalid for s in solves]
        missing = Challenges.query.filter( not_(Challenges.id.in_(solve_ids) ) ).all()
        addrs = Tracking.query.filter_by(team=teamid).order_by(Tracking.date.desc()).group_by(Tracking.ip).all()
        wrong_keys = WrongKeys.query.filter_by(teamid=teamid).order_by(WrongKeys.date.asc()).all()
        awards = Awards.query.filter_by(teamid=teamid).order_by(Awards.date.asc()).all()
        score = user.score()
        place = user.place()
        return render_template('admin/team.html', solves=solves, team=user, addrs=addrs, score=score, missing=missing,
                               place=place, wrong_keys=wrong_keys, awards=awards)
    elif request.method == 'POST':
        admin_user = request.form.get('admin', None)
        if admin_user:
            admin_user = 1 if admin_user == "true" else 0
            user.admin = admin_user
            user.banned = admin_user
            db.session.commit()
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
            return jsonify({'data':errors})
        else:
            user.name = name
            user.email = email
            if password:
                user.password = bcrypt_sha256.encrypt(password)
            user.website = website
            user.affiliation = affiliation
            user.country = country
            db.session.commit()
            db.session.close()
            return jsonify({'data':['success']})


@admin.route('/admin/team/<teamid>/mail', methods=['POST'])
@admins_only
def email_user(teamid):
    message = request.form.get('msg', None)
    team = Teams.query.filter(Teams.id == teamid).first()
    if message and team:
        if sendmail(team.email, message):
            return "1"
    return "0"


@admin.route('/admin/team/<teamid>/ban', methods=['POST'])
@admins_only
def ban(teamid):
    user = Teams.query.filter_by(id=teamid).first()
    user.banned = 1
    db.session.commit()
    return redirect(url_for('admin.admin_scoreboard'))


@admin.route('/admin/team/<teamid>/unban', methods=['POST'])
@admins_only
def unban(teamid):
    user = Teams.query.filter_by(id=teamid).first()
    user.banned = None
    db.session.commit()
    return redirect(url_for('admin.admin_scoreboard'))


@admin.route('/admin/team/<teamid>/delete', methods=['POST'])
@admins_only
def delete_team(teamid):
    try:
        WrongKeys.query.filter_by(teamid=teamid).delete()
        Solves.query.filter_by(teamid=teamid).delete()
        Tracking.query.filter_by(team=teamid).delete()
        Teams.query.filter_by(id=teamid).delete()
        db.session.commit()
    except DatabaseError:
        return '0'
    else:
        return '1'


@admin.route('/admin/graphs/<graph_type>')
@admins_only
def admin_graph(graph_type):
    if graph_type == 'categories':
        categories = db.session.query(Challenges.category, db.func.count(Challenges.category)).group_by(Challenges.category).all()
        json_data = {'categories':[]}
        for category, count in categories:
            json_data['categories'].append({'category':category, 'count':count})
        return jsonify(json_data)
    elif graph_type == "solves":
        solves = Solves.query.join(Teams).filter(Teams.banned==None).add_columns(db.func.count(Solves.chalid)).group_by(Solves.chalid).all()
        json_data = {}
        for chal, count in solves:
            json_data[chal.chal.name] = count
        return jsonify(json_data)


@admin.route('/admin/scoreboard')
@admins_only
def admin_scoreboard():
    score = db.func.sum(Challenges.value).label('score')
    scores = db.session.query(Solves.teamid.label('teamid'), Teams.name.label('name'), score, Solves.date.label('date')) \
        .join(Teams) \
        .join(Challenges) \
        .filter(Teams.banned == None) \
        .group_by(Solves.teamid)

    awards = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'),
                              db.func.sum(Awards.value).label('score'), Awards.date.label('date')) \
        .filter(Teams.id == Awards.teamid) \
        .group_by(Teams.id)

    results = union_all(scores, awards)

    standings = db.session.query(results.columns.teamid, results.columns.name,
                                 db.func.sum(results.columns.score).label('score')) \
        .group_by(results.columns.teamid) \
        .order_by(db.func.sum(results.columns.score).desc(), db.func.max(results.columns.date)) \
        .all()
    db.session.close()
    return render_template('admin/scoreboard.html', teams=standings)


@admin.route('/admin/teams/<teamid>/awards', methods=['GET'])
@admins_only
def admin_awards(teamid):
    awards = Awards.query.filter_by(teamid=teamid).all()

    awards_list = []
    for award in awards:
        awards_list.append({
                'id':award.id,
                'name':award.name,
                'description':award.description,
                'date':award.date,
                'value':award.value,
                'category':award.category,
                'icon':award.icon
            })
    json_data = {'awards':awards_list}
    return jsonify(json_data)


@admin.route('/admin/awards/add', methods=['POST'])
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
        return "1"
    except Exception as e:
        print e
        return "0"


@admin.route('/admin/awards/<award_id>/delete', methods=['POST'])
@admins_only
def delete_award(award_id):
    try:
        award = Awards.query.filter_by(id=award_id).first()
        db.session.delete(award)
        db.session.commit()
        return '1'
    except Exception as e:
        print e
        return "0"


@admin.route('/admin/scores')
@admins_only
def admin_scores():
    score = db.func.sum(Challenges.value).label('score')
    quickest = db.func.max(Solves.date).label('quickest')
    teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
    db.session.close()
    json_data = {'teams':[]}
    for i, x in enumerate(teams):
        json_data['teams'].append({'place':i+1, 'id':x.teamid, 'name':x.name,'score':int(x.score)})
    return jsonify(json_data)


@admin.route('/admin/solves/<teamid>', methods=['GET'])
@admins_only
def admin_solves(teamid="all"):
    if teamid == "all":
        solves = Solves.query.all()
    else:
        solves = Solves.query.filter_by(teamid=teamid).all()
        awards = Awards.query.filter_by(teamid=teamid).all()
    db.session.close()
    json_data = {'solves':[]}
    for x in solves:
        json_data['solves'].append({
            'id': x.id,
            'chal': x.chal.name,
            'chalid': x.chalid,
            'team': x.teamid,
            'value': x.chal.value,
            'category': x.chal.category,
            'time': unix_time(x.date)
        })
    for award in awards:
        json_data['solves'].append({
            'chal': award.name,
            'chalid': None,
            'team': award.teamid,
            'value': award.value,
            'category': award.category,
            'time': unix_time(award.date)
        })
    json_data['solves'].sort(key=lambda k:k['time'])
    return jsonify(json_data)


@admin.route('/admin/solves/<teamid>/<chalid>/solve', methods=['POST'])
@admins_only
def create_solve(teamid, chalid):
    solve = Solves(chalid=chalid, teamid=teamid, ip='127.0.0.1', flag='MARKED_AS_SOLVED_BY_ADMIN')
    db.session.add(solve)
    db.session.commit()
    db.session.close()
    return '1'

@admin.route('/admin/solves/<teamid>/<chalid>/delete', methods=['POST'])
@admins_only
def delete_solve(teamid, chalid):
    solve = Solves.query.filter_by(teamid=teamid, chalid=chalid).first()
    db.session.delete(solve)
    db.session.commit()
    db.session.close()
    return '1'


@admin.route('/admin/wrong_keys/<teamid>/<chalid>/delete', methods=['POST'])
@admins_only
def delete_wrong_key(teamid, chalid):
    wrong_key = WrongKeys.query.filter_by(teamid=teamid, chalid=chalid).first()
    db.session.delete(wrong_key)
    db.session.commit()
    return '1'


@admin.route('/admin/statistics', methods=['GET'])
@admins_only
def admin_stats():
    db.session.commit()

    teams_registered = db.session.query(db.func.count(Teams.id)).first()[0]
    wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    challenge_count = db.session.query(db.func.count(Challenges.id)).first()[0]
    most_solved_chal = Solves.query.add_columns(db.func.count(Solves.chalid).label('solves')).group_by(Solves.chalid).order_by('solves DESC').first()
    least_solved_chal = Challenges.query.add_columns(db.func.count(Solves.chalid).label('solves')).outerjoin(Solves).group_by(Challenges.id).order_by('solves ASC').first()

    db.session.close()

    return render_template('admin/statistics.html', team_count=teams_registered,
        wrong_count=wrong_count,
        solve_count=solve_count,
        challenge_count=challenge_count,
        most_solved=most_solved_chal,
        least_solved=least_solved_chal
        )


@admin.route('/admin/wrong_keys/<page>', methods=['GET'])
@admins_only
def admin_wrong_key(page='1'):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page

    wrong_keys = WrongKeys.query.add_columns(WrongKeys.chalid, WrongKeys.flag, WrongKeys.teamid, WrongKeys.date,\
                Challenges.name.label('chal_name'), Teams.name.label('team_name')).\
                join(Challenges).join(Teams).order_by('team_name ASC').slice(page_start, page_end).all()

    wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
    pages = int(wrong_count / results_per_page) + (wrong_count % results_per_page > 0)

    return render_template('admin/wrong_keys.html', wrong_keys=wrong_keys, pages=pages, curr_page=page)


@admin.route('/admin/correct_keys/<page>', methods=['GET'])
@admins_only
def admin_correct_key(page='1'):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    solves = Solves.query.add_columns(Solves.chalid, Solves.teamid, Solves.date, Solves.flag, \
                Challenges.name.label('chal_name'), Teams.name.label('team_name')).\
                join(Challenges).join(Teams).order_by('team_name ASC').slice(page_start, page_end).all()

    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    pages = int(solve_count / results_per_page) + (solve_count % results_per_page > 0)

    return render_template('admin/correct_keys.html', solves=solves, pages=pages, curr_page=page)


@admin.route('/admin/fails/<teamid>', methods=['GET'])
@admins_only
def admin_fails(teamid='all'):
    if teamid == "all":
        fails = WrongKeys.query.join(Teams, WrongKeys.teamid == Teams.id).filter(Teams.banned==None).count()
        solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Teams.banned==None).count()
        db.session.close()
        json_data = {'fails':str(fails), 'solves': str(solves)}
        return jsonify(json_data)
    else:
        fails = WrongKeys.query.filter_by(teamid=teamid).count()
        solves = Solves.query.filter_by(teamid=teamid).count()
        db.session.close()
        json_data = {'fails':str(fails), 'solves': str(solves)}
        return jsonify(json_data)


@admin.route('/admin/chal/new', methods=['POST'])
@admins_only
def admin_create_chal():
    files = request.files.getlist('files[]')

    ## TODO: Expand to support multiple flags
    flags = [{'flag':request.form['key'], 'type':int(request.form['key_type[0]'])}]

    # Create challenge
    chal = Challenges(request.form['name'], request.form['desc'], request.form['value'], request.form['category'], flags)
    if 'hidden' in request.form:
        chal.hidden = True
    else:
        chal.hidden = False
    db.session.add(chal)
    db.session.commit()

    for f in files:
        filename = secure_filename(f.filename)

        if len(filename) <= 0:
            continue

        md5hash = hashlib.md5(os.urandom(64)).hexdigest()

        if not os.path.exists(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash)):
            os.makedirs(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash))

        f.save(os.path.join(os.path.normpath(app.static_folder), 'uploads', md5hash, filename))
        db_f = Files(chal.id, os.path.join('static', 'uploads', md5hash, filename))
        db.session.add(db_f)

    db.session.commit()
    db.session.close()
    return redirect(url_for('admin.admin_chals'))


@admin.route('/admin/chal/delete', methods=['POST'])
@admins_only
def admin_delete_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first()
    if challenge:
        WrongKeys.query.filter_by(chalid=challenge.id).delete()
        Solves.query.filter_by(chalid=challenge.id).delete()
        Keys.query.filter_by(chal=challenge.id).delete()
        files = Files.query.filter_by(chal=challenge.id).all()
        Files.query.filter_by(chal=challenge.id).delete()
        for file in files:
            folder = os.path.dirname(file.location)
            rmdir(folder)
        Tags.query.filter_by(chal=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()
        db.session.close()
    return '1'


@admin.route('/admin/chal/update', methods=['POST'])
@admins_only
def admin_update_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first()
    challenge.name = request.form['name']
    challenge.description = request.form['desc']
    challenge.value = request.form['value']
    challenge.category = request.form['category']
    challenge.hidden = 'hidden' in request.form
    db.session.add(challenge)
    db.session.commit()
    db.session.close()
    return redirect(url_for('admin.admin_chals'))
