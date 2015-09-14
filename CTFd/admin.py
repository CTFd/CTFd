from flask import render_template, request, redirect, abort, jsonify, url_for, session
from CTFd.utils import sha512, is_safe_url, authed, admins_only, is_admin, unix_time, unix_time_millis, get_config, set_config, get_digitalocean, sendmail, rmdir
from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config
from itsdangerous import TimedSerializer, BadTimeSignature
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

def init_admin(app):
    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if request.method == 'POST':
            username = request.form.get('name')
            password = request.form.get('password')

            admin = Teams.query.filter_by(name=request.form['name'], admin=True).first()
            if admin and bcrypt_sha256.verify(request.form['password'], admin.password):
                try:
                    session.regenerate() # NO SESSION FIXATION FOR YOU
                except:
                    pass # TODO: Some session objects dont implement regenerate :(
                session['username'] = admin.name
                session['id'] = admin.id
                session['admin'] = True
                session['nonce'] = sha512(os.urandom(10))
                db.session.close()
                return redirect('/admin/graphs')

        if is_admin():
            return redirect('/admin/graphs')

        return render_template('admin/login.html')

    @app.route('/admin/graphs')
    @admins_only
    def admin_graphs():
        return render_template('admin/graphs.html')

    @app.route('/admin/config', methods=['GET', 'POST'])
    @admins_only
    def admin_config():
        if request.method == "POST":
            try:
                start = int(request.form['start'])
                end = int(request.form['end'])
            except (ValueError, TypeError):
                start = None
                end = None

            try:
                view_challenges_unregistered = bool(request.form.get('view_challenges_unregistered', None))
                prevent_registration = bool(request.form.get('prevent_registration', None))
                prevent_name_change = bool(request.form.get('prevent_name_change', None))
                view_after_ctf = bool(request.form.get('view_after_ctf', None))
            except (ValueError, TypeError):
                view_challenges_unregistered = None
                prevent_registration = None
                prevent_name_change = None
                view_after_ctf = None
            finally:
                view_challenges_unregistered = set_config('view_challenges_unregistered', view_challenges_unregistered)
                prevent_registration = set_config('prevent_registration', prevent_registration)
                prevent_name_change = set_config('prevent_name_change', prevent_name_change)
                view_after_ctf = set_config('view_after_ctf', view_after_ctf)

            ctf_name = set_config("ctf_name", request.form.get('ctf_name', None))
            mg_api_key = set_config("mg_api_key", request.form.get('mg_api_key', None))
            do_api_key = set_config("do_api_key", request.form.get('do_api_key', None))
            max_tries = set_config("max_tries", request.form.get('max_tries', None))


            db_start = Config.query.filter_by(key='start').first()
            db_start.value = start

            db_end = Config.query.filter_by(key='end').first()
            db_end.value = end

            db.session.add(db_start)
            db.session.add(db_end)

            db.session.commit()
            return redirect('/admin/config')

        ctf_name = get_config('ctf_name')
        if not ctf_name:
            set_config('do_api_key', None)

        mg_api_key = get_config('do_api_key')
        if not mg_api_key:
            set_config('do_api_key', None)

        do_api_key = get_config('do_api_key')
        if not do_api_key:
            set_config('do_api_key', None)

        max_tries = get_config('max_tries')
        if not max_tries:
            set_config('max_tries', 0)
            max_tries = 0

        view_after_ctf = get_config('view_after_ctf') == '1'
        if not view_after_ctf:
            set_config('view_after_ctf', 0)
            view_after_ctf = 0

        start = get_config('start')
        if not start:
            set_config('start', None)

        end = get_config('end')
        if not end:
            set_config('end', None)

        view_challenges_unregistered = get_config('view_challenges_unregistered') == '1'
        if not view_challenges_unregistered:
            set_config('view_challenges_unregistered', None)

        prevent_registration = get_config('prevent_registration') == '1'
        if not prevent_registration:
            set_config('prevent_registration', None)

        prevent_name_change = get_config('prevent_name_change') == '1'
        if not prevent_name_change:
            set_config('prevent_name_change', None)

        db.session.commit()
        db.session.close()

        return render_template('admin/config.html', ctf_name=ctf_name, start=start, end=end,
                               max_tries=max_tries,
                               view_challenges_unregistered=view_challenges_unregistered,
                               prevent_registration=prevent_registration, do_api_key=do_api_key, mg_api_key=mg_api_key,
                               prevent_name_change=prevent_name_change,
                               view_after_ctf=view_after_ctf)

    @app.route('/admin/pages', defaults={'route': None}, methods=['GET', 'POST'])
    @app.route('/admin/pages/<route>', methods=['GET', 'POST'])
    @admins_only
    def admin_pages(route):
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
                return redirect('/admin/pages')
            page = Pages(route, html)
            db.session.add(page)
            db.session.commit()
            return redirect('/admin/pages')
        if not route and request.method == 'POST':
            return render_template('admin/editor.html')
        pages = Pages.query.all()
        return render_template('admin/pages.html', routes=pages)

    @app.route('/admin/page/<pageroute>/delete', methods=['POST'])
    @admins_only
    def delete_page(pageroute):
        page = Pages.query.filter_by(route=pageroute).first()
        db.session.delete(page)
        db.session.commit()
        return '1'

    @app.route('/admin/hosts', methods=['GET'])
    @admins_only
    def admin_hosts():
        m = get_digitalocean()
        errors = []
        if not m:
            errors.append("Your Digital Ocean API key is not set")
            return render_template('admin/hosts.html', errors=errors)

        hosts = m.get_all_droplets()
        slugs = m.get_all_sizes()
        images = m.get_all_images()
        regions = m.get_all_regions()

        return render_template('admin/hosts.html', hosts=hosts, slugs=slugs, images=images, regions=regions)

    @app.route('/admin/chals', methods=['POST', 'GET'])
    @admins_only
    def admin_chals():
        if request.method == 'POST':
            chals = Challenges.query.add_columns('id', 'name', 'value', 'description', 'category').order_by(Challenges.value).all()
            
            json = {'game':[]}
            for x in chals:
                json['game'].append({'id':x[1], 'name':x[2], 'value':x[3], 'description':x[4], 'category':x[5]})

            db.session.close()
            return jsonify(json)
        else:
            return render_template('admin/chals.html')

    @app.route('/admin/keys/<chalid>', methods=['POST', 'GET'])
    @admins_only
    def admin_keys(chalid):
        if request.method == 'GET':
            keys = Keys.query.filter_by(chal=chalid).all()
            json = {'keys':[]}
            for x in keys:
                json['keys'].append({'id':x.id, 'key':x.flag, 'type':x.key_type})
            return jsonify(json)
        elif request.method == 'POST':
            keys = Keys.query.filter_by(chal=chalid).all()
            for x in keys:
                db.session.delete(x)

            newkeys = request.form.getlist('keys[]')
            newvals = request.form.getlist('vals[]')
            for flag, val in zip(newkeys, newvals):
                key = Keys(chalid, flag, val)
                db.session.add(key)

            db.session.commit()
            db.session.close()
            return '1'

    @app.route('/admin/tags/<chalid>', methods=['GET', 'POST'])
    @admins_only
    def admin_tags(chalid):
        if request.method == 'GET':
            tags = Tags.query.filter_by(chal=chalid).all()
            json = {'tags':[]}
            for x in tags:
                 json['tags'].append({'id':x.id, 'chal':x.chal, 'tag':x.tag})
            return jsonify(json)

        elif request.method == 'POST':
            newtags = request.form.getlist('tags[]')
            for x in newtags:
                tag = Tags(chalid, x)
                db.session.add(tag)
            db.session.commit()
            db.session.close()
            return '1'

    @app.route('/admin/tags/<tagid>/delete', methods=['POST'])
    @admins_only
    def admin_delete_tags(tagid):
        if request.method == 'POST':
            tag = Tags.query.filter_by(id=tagid).first_or_404()
            db.session.delete(tag)
            db.session.commit()
            db.session.close()
            return "1"


    @app.route('/admin/files/<chalid>', methods=['GET', 'POST'])
    @admins_only
    def admin_files(chalid):
        if request.method == 'GET':
            files = Files.query.filter_by(chal=chalid).all()
            json = {'files':[]}
            for x in files:
                json['files'].append({'id':x.id, 'file':x.location})
            return jsonify(json)
        if request.method == 'POST':
            if request.form['method'] == "delete":
                f = Files.query.filter_by(id=request.form['file']).first_or_404()
                if os.path.isfile(f.location):
                    os.unlink(f.location)
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

                    # BUG NEEDS TO GO TO S3
                    base = os.path.dirname(os.path.dirname(__file__))
                    ## mod_wsgi does some sad things with cwd so the upload directory needs to be shifted a bit
                    if not os.path.exists(os.path.join(base, app.config['UPLOAD_FOLDER'], md5hash)):
                        os.makedirs(os.path.join(base, app.config['UPLOAD_FOLDER'], md5hash))

                    f.save(os.path.join(base, app.config['UPLOAD_FOLDER'], md5hash, filename))

                    ## This needs to be relative to CTFd so doesn't nee base.
                    db_f = Files(chalid, os.path.join(app.config['UPLOAD_FOLDER'], md5hash, filename))
                    db.session.add(db_f)

                db.session.commit()
                db.session.close()
                return redirect('/admin/chals')

    @app.route('/admin/teams')
    @admins_only
    def admin_teams():
        teams = Teams.query.all()
        return render_template('admin/teams.html', teams=teams)

    @app.route('/admin/team/<teamid>', methods=['GET', 'POST'])
    @admins_only
    def admin_team(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        solves = Solves.query.filter_by(teamid=teamid).all()
        addrs = Tracking.query.filter_by(team=teamid).group_by(Tracking.ip).all()
        score = user.score()
        place = user.place()

        if request.method == 'GET':
            return render_template('admin/team.html', solves=solves, team=user, addrs=addrs, score=score, place=place)
        elif request.method == 'POST':
            admin = request.form.get('admin', "false")
            admin = 1 if admin == "true" else 0
            if admin:
                user.admin = 1
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

    @app.route('/admin/team/<teamid>/mail', methods=['POST'])
    @admins_only
    def email_user(teamid):
        message = request.form.get('msg', None)
        team = Teams.query.filter(Teams.id == teamid).first()
        if message and team:
            if sendmail(team.email, message):
                return "1"
        return "0"

    @app.route('/admin/team/<teamid>/ban', methods=['POST'])
    @admins_only
    def ban(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        user.banned = 1
        db.session.commit()
        return redirect('/admin/scoreboard')

    @app.route('/admin/team/<teamid>/unban', methods=['POST'])
    @admins_only
    def unban(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        user.banned = None
        db.session.commit()
        return redirect('/admin/scoreboard')

    @app.route('/admin/team/<teamid>/delete', methods=['POST'])
    @admins_only
    def delete_team(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        db.session.delete(user)
        db.session.commit()
        return '1'


    @app.route('/admin/graphs/<graph_type>')
    @admins_only
    def admin_graph(graph_type):
        if graph_type == 'categories':
            categories = db.session.query(Challenges.category, db.func.count(Challenges.category)).group_by(Challenges.category).all()
            json = {'categories':[]}
            for category, count in categories:
                json['categories'].append({'category':category, 'count':count})
            return jsonify(json)
        elif graph_type == "solves":
            solves = Solves.query.add_columns(db.func.count(Solves.chalid)).group_by(Solves.chalid).all()
            json = {}        
            for chal, count in solves:
                json[chal.chal.name] = count
            return jsonify(json)

    @app.route('/admin/scoreboard')
    @admins_only
    def admin_scoreboard():
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, Teams.banned, score).join(Teams).join(Challenges).group_by(Solves.teamid).order_by(score.desc(), quickest)
        db.session.close()
        return render_template('admin/scoreboard.html', teams=teams)

    @app.route('/admin/scores')
    @admins_only
    def admin_scores():
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
        db.session.close()
        json = {'teams':[]}
        for i, x in enumerate(teams):
            json['teams'].append({'place':i+1, 'id':x.teamid, 'name':x.name,'score':int(x.score)})
        return jsonify(json)

    @app.route('/admin/solves/<teamid>', methods=['GET'])
    @admins_only
    def admin_solves(teamid="all"):
        if teamid == "all":
            solves = Solves.query.all()
        else:
            solves = Solves.query.filter_by(teamid=teamid).all()
        db.session.close()
        json = {'solves':[]}
        for x in solves:
            json['solves'].append({'id':x.id, 'chal':x.chal.name, 'chalid':x.chalid,'team':x.teamid, 'value': x.chal.value, 'category':x.chal.category, 'time':unix_time(x.date)})
        return jsonify(json)


    @app.route('/admin/solves/<teamid>/<chalid>/delete', methods=['POST'])
    @admins_only
    def delete_solve(teamid, chalid):
        solve = Solves.query.filter_by(teamid=teamid, chalid=chalid).first()
        db.session.delete(solve)
        db.session.commit()
        return '1'

    @app.route('/admin/statistics', methods=['GET'])
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

    @app.route('/admin/wrong_keys/<page>', methods=['GET'])
    @admins_only
    def admin_wrong_key(page='1'):
        page = abs(int(page))
        results_per_page = 50
        page_start = results_per_page * ( page - 1 )
        page_end = results_per_page * ( page - 1 ) + results_per_page

        wrong_keys = WrongKeys.query.add_columns(WrongKeys.flag, WrongKeys.team, WrongKeys.date,\
                    Challenges.name.label('chal_name'), Teams.name.label('team_name')).\
                    join(Challenges).join(Teams).order_by('team_name ASC').slice(page_start, page_end).all()

        wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
        pages = int(wrong_count / results_per_page) + (wrong_count % results_per_page > 0)

        return render_template('admin/wrong_keys.html', wrong_keys=wrong_keys, pages=pages)

    @app.route('/admin/correct_keys/<page>', methods=['GET'])
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

        return render_template('admin/correct_keys.html', solves=solves, pages=pages)

    @app.route('/admin/fails/<teamid>', methods=['GET'])
    @admins_only
    def admin_fails(teamid='all'):
        if teamid == "all":
            fails = WrongKeys.query.count()
            solves = Solves.query.count()
            db.session.close()
            json = {'fails':str(fails), 'solves': str(solves)}
            return jsonify(json)
        else:
            fails = WrongKeys.query.filter_by(team=teamid).count()
            solves = Solves.query.filter_by(teamid=teamid).count()
            db.session.close()
            json = {'fails':str(fails), 'solves': str(solves)}
            return jsonify(json)
        


    @app.route('/admin/chal/new', methods=['POST'])
    def admin_create_chal():
        files = request.files.getlist('files[]')

        # Create challenge
        chal = Challenges(request.form['name'], request.form['desc'], request.form['value'], request.form['category'])
        db.session.add(chal)
        db.session.commit()

        # Add keys
        key = Keys(chal.id, request.form['key'], request.form['key_type[0]'])
        db.session.add(key)
        db.session.commit()

        for f in files:
            filename = secure_filename(f.filename)

            if len(filename) <= 0:
                continue

            md5hash = hashlib.md5(filename).hexdigest()

            if not os.path.exists(os.path.join(os.path.normpath(app.config['UPLOAD_FOLDER']), md5hash)):
                os.makedirs(os.path.join(os.path.normpath(app.config['UPLOAD_FOLDER']), md5hash))

            f.save(os.path.join(os.path.normpath(app.config['UPLOAD_FOLDER']), md5hash, filename))
            db_f = Files(chal.id, os.path.join(os.path.normpath(app.config['UPLOAD_FOLDER']), md5hash, filename))
            db.session.add(db_f)

        db.session.commit()
        db.session.close()
        return redirect('/admin/chals')

    @app.route('/admin/chal/delete', methods=['POST'])
    def admin_delete_chal():
        challenge = Challenges.query.filter_by(id=request.form['id']).first()
        if challenge:
            WrongKeys.query.filter_by(chal=challenge.id).delete()
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

    @app.route('/admin/chal/update', methods=['POST'])
    def admin_update_chal():
        challenge = Challenges.query.filter_by(id=request.form['id']).first()
        challenge.name = request.form['name']
        challenge.description = request.form['desc']
        challenge.value = request.form['value']
        challenge.category = request.form['category']
        db.session.add(challenge)
        db.session.commit()
        db.session.close()
        return redirect('/admin/chals')
