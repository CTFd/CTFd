from flask import render_template, request, redirect, abort, jsonify, url_for, session, Blueprint
from CTFd.utils import sha512, is_safe_url, authed, admins_only, is_admin, unix_time, unix_time_millis, get_config, \
    set_config, sendmail, rmdir, create_image, delete_image, run_image, container_status, container_ports, \
    container_stop, container_start, get_themes, cache
from CTFd.models import db, Teams, Solves, Awards, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError
from CTFd.scoreboard import get_standings
from itsdangerous import TimedSerializer, BadTimeSignature
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import union_all
from sqlalchemy.sql.functions import coalesce
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
        ctf_theme = set_config("ctf_theme", request.form.get('ctf_theme', None))

        mailfrom_addr = set_config("mailfrom_addr", request.form.get('mailfrom_addr', None))
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
        db.session.close()
        with app.app_context():
            cache.clear()
        return redirect(url_for('admin.admin_config'))

    with app.app_context():
        cache.clear()
    ctf_name = get_config('ctf_name')
    ctf_theme = get_config('ctf_theme')
    max_tries = get_config('max_tries')

    mail_server = get_config('mail_server')
    mail_port = get_config('mail_port')
    mail_username = get_config('mail_username')
    mail_password = get_config('mail_password')

    mailfrom_addr = get_config('mailfrom_addr')
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

    themes = get_themes()
    themes.remove(ctf_theme)

    return render_template('admin/config.html',
                           ctf_name=ctf_name,
                           ctf_theme_config=ctf_theme,
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
                           mailfrom_addr=mailfrom_addr,
                           mg_base_url=mg_base_url,
                           mg_api_key=mg_api_key,
                           prevent_name_change=prevent_name_change,
                           verify_emails=verify_emails,
                           view_after_ctf=view_after_ctf,
                           themes=themes)


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
            db.session.close()
            return redirect(url_for('admin.admin_pages'))
        page = Pages(route, html)
        db.session.add(page)
        db.session.commit()
        db.session.close()
        return redirect(url_for('admin.admin_pages'))
    pages = Pages.query.all()
    return render_template('admin/pages.html', routes=pages, css=get_config('css'))


@admin.route('/admin/page/<pageroute>/delete', methods=['POST'])
@admins_only
def delete_page(pageroute):
    page = Pages.query.filter_by(route=pageroute).first()
    db.session.delete(page)
    db.session.commit()
    db.session.close()
    return '1'


@admin.route('/admin/containers', methods=['GET'])
@admins_only
def list_container():
    containers = Containers.query.all()
    for c in containers:
        c.status = container_status(c.name)
        c.ports = ", ".join(container_ports(c.name, verbose=True))
    return render_template('admin/containers.html', containers=containers)


@admin.route('/admin/containers/<container_id>/stop', methods=['POST'])
@admins_only
def stop_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if container_stop(container.name):
        return '1'
    else:
        return '0'


@admin.route('/admin/containers/<container_id>/start', methods=['POST'])
@admins_only
def run_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if container_status(container.name) == 'missing':
        if run_image(container.name):
            return '1'
        else:
            return '0'
    else:
        if container_start(container.name):
            return '1'
        else:
            return '0'


@admin.route('/admin/containers/<container_id>/delete', methods=['POST'])
@admins_only
def delete_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if delete_image(container.name):
        db.session.delete(container)
        db.session.commit()
        db.session.close()
    return '1'


@admin.route('/admin/containers/new', methods=['POST'])
@admins_only
def new_container():
    name = request.form.get('name')
    if set(name) <= set('abcdefghijklmnopqrstuvwxyz0123456789-_'):
        return redirect(url_for('admin.list_container'))
    buildfile = request.form.get('buildfile')
    files = request.files.getlist('files[]')
    create_image(name=name, buildfile=buildfile, files=files)
    run_image(name)
    return redirect(url_for('admin.list_container'))



@admin.route('/admin/chals', methods=['POST', 'GET'])
@admins_only
def admin_chals():
    if request.method == 'POST':
        chals = Challenges.query.add_columns('id', 'name', 'value', 'description', 'category', 'hidden').order_by(Challenges.value).all()

        teams_with_points = db.session.query(Solves.teamid).join(Teams).filter(
            Teams.banned == False).group_by(
                Solves.teamid).count()

        json_data = {'game':[]}
        for x in chals:
            solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid == x[1], Teams.banned == False).count()
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
            if os.path.exists(os.path.join(app.root_path, 'uploads', f.location)): ## Some kind of os.path.isfile issue on Windows...
                os.unlink(os.path.join(app.root_path, 'uploads', f.location))
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

                if not os.path.exists(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash)):
                    os.makedirs(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash))

                f.save(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash, filename))
                db_f = Files(chalid, (md5hash + '/' + filename))
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

    teams = Teams.query.order_by(Teams.id.asc()).slice(page_start, page_end).all()
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
        last_seen = db.func.max(Tracking.date).label('last_seen')
        addrs = db.session.query(Tracking.ip, last_seen) \
                .filter_by(team=teamid) \
                .group_by(Tracking.ip) \
                .order_by(last_seen.desc()).all()
        wrong_keys = WrongKeys.query.filter_by(teamid=teamid).order_by(WrongKeys.date.asc()).all()
        awards = Awards.query.filter_by(teamid=teamid).order_by(Awards.date.asc()).all()
        score = user.score()
        place = user.place()
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
    user.banned = True
    db.session.commit()
    db.session.close()
    return redirect(url_for('admin.admin_scoreboard'))


@admin.route('/admin/team/<teamid>/unban', methods=['POST'])
@admins_only
def unban(teamid):
    user = Teams.query.filter_by(id=teamid).first()
    user.banned = False
    db.session.commit()
    db.session.close()
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
        db.session.close()
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
        solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves_cnt')) \
                .join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False) \
                .group_by(Solves.chalid).subquery()
        solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves_cnt, Challenges.name) \
                .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
        json_data = {}
        for chal, count, name in solves:
            json_data[name] = count
        return jsonify(json_data)


@admin.route('/admin/scoreboard')
@admins_only
def admin_scoreboard():
    standings = get_standings(admin=True)
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
        db.session.close()
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
        db.session.close()
        return '1'
    except Exception as e:
        print e
        return "0"


@admin.route('/admin/scores')
@admins_only
def admin_scores():
    score = db.func.sum(Challenges.value).label('score')
    quickest = db.func.max(Solves.date).label('quickest')
    teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == False).group_by(Solves.teamid).order_by(score.desc(), quickest)
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

@admin.route('/admin/solves/<keyid>/delete', methods=['POST'])
@admins_only
def delete_solve(keyid):
    solve = Solves.query.filter_by(id=keyid).first_or_404()
    db.session.delete(solve)
    db.session.commit()
    db.session.close()
    return '1'


@admin.route('/admin/wrong_keys/<keyid>/delete', methods=['POST'])
@admins_only
def delete_wrong_key(keyid):
    wrong_key = WrongKeys.query.filter_by(id=keyid).first_or_404()
    db.session.delete(wrong_key)
    db.session.commit()
    db.session.close()
    return '1'



@admin.route('/admin/statistics', methods=['GET'])
@admins_only
def admin_stats():
    teams_registered = db.session.query(db.func.count(Teams.id)).first()[0]
    wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    challenge_count = db.session.query(db.func.count(Challenges.id)).first()[0]

    solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves_cnt')) \
        .join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False) \
        .group_by(Solves.chalid).subquery()
    solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves_cnt, Challenges.name) \
        .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
    solve_data = {}
    for chal, count, name in solves:
        solve_data[name] = count

    most_solved = None
    least_solved = None
    if len(solve_data):
        most_solved = max(solve_data, key=solve_data.get)
        least_solved = min(solve_data, key=solve_data.get)
        
    db.session.expunge_all()
    db.session.commit()
    db.session.close()

    return render_template('admin/statistics.html', team_count=teams_registered,
        wrong_count=wrong_count,
        solve_count=solve_count,
        challenge_count=challenge_count,
        solve_data=solve_data,
        most_solved=most_solved,
        least_solved=least_solved
        )


@admin.route('/admin/wrong_keys/<page>', methods=['GET'])
@admins_only
def admin_wrong_key(page='1'):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page

    wrong_keys = WrongKeys.query.add_columns(WrongKeys.id, WrongKeys.chalid, WrongKeys.flag, WrongKeys.teamid, WrongKeys.date,\
                Challenges.name.label('chal_name'), Teams.name.label('team_name')).\
                join(Challenges).join(Teams).order_by(WrongKeys.date.desc()).slice(page_start, page_end).all()

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

    solves = Solves.query.add_columns(Solves.id, Solves.chalid, Solves.teamid, Solves.date, Solves.flag, \
                Challenges.name.label('chal_name'), Teams.name.label('team_name')).\
                join(Challenges).join(Teams).order_by(Solves.date.desc()).slice(page_start, page_end).all()

    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    pages = int(solve_count / results_per_page) + (solve_count % results_per_page > 0)

    return render_template('admin/correct_keys.html', solves=solves, pages=pages, curr_page=page)


@admin.route('/admin/fails/<teamid>', methods=['GET'])
@admins_only
def admin_fails(teamid='all'):
    if teamid == "all":
        fails = WrongKeys.query.join(Teams, WrongKeys.teamid == Teams.id).filter(Teams.banned == False).count()
        solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False).count()
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

        if not os.path.exists(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash)):
            os.makedirs(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash))

        f.save(os.path.join(os.path.normpath(app.root_path), 'uploads', md5hash, filename))
        db_f = Files(chal.id, (md5hash + '/' + filename))
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
            folder = os.path.dirname(os.path.join(os.path.normpath(app.root_path), 'uploads', file.location))
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
