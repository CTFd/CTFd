from flask import render_template, request, redirect, abort, jsonify, url_for, session
from CTFd.utils import sha512, is_safe_url, authed, admins_only, is_admin, unix_time, unix_time_millis
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
                session.regenerate() # NO SESSION FIXATION FOR YOU
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
            except (ValueError, TypeError):
                view_challenges_unregistered = None

            print repr(start), repr(end), repr(view_challenges_unregistered)

            db_start = Config.query.filter_by(key='start').first()
            db_start.value = start

            db_end = Config.query.filter_by(key='end').first()
            db_end.value = end

            db_view_challenges_unregistered = Config.query.filter_by(key='view_challenges_unregistered').first()
            db_view_challenges_unregistered.value = view_challenges_unregistered

            db.session.add(db_start)
            db.session.add(db_end)
            db.session.add(db_view_challenges_unregistered)

            db.session.commit()
            return redirect('/admin/config')

        start = Config.query.filter_by(key="start").first()
        if start:
            start = start.value
        else:
            start = Config('start', None)
            db.session.add(start)

        end = Config.query.filter_by(key="end").first()
        if end:
            end = end.value
        else:
            end = Config('end', None)
            db.session.add(end)

        view_challenges_unregistered = Config.query.filter_by(key='view_challenges_unregistered').first()
        if view_challenges_unregistered:
            view_challenges_unregistered = (view_challenges_unregistered.value == '1')
        else:
            view_challenges_unregistered = Config('view_challenges_unregistered', None)
            db.session.add(view_challenges_unregistered)

        db.session.commit()
        db.session.close()

        return render_template('admin/config.html', start=start, end=end, view_challenges_unregistered=view_challenges_unregistered)

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


    @app.route('/admin/chals', methods=['POST', 'GET'])
    @admins_only
    def admin_chals():
        # if authed():
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
                    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], md5hash)):
                        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], md5hash))

                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], md5hash, filename))
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

        if request.method == 'GET':
            return render_template('admin/team.html', solves=solves, team=user, addrs=addrs)
        elif request.method == 'POST':
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
                    user.password = bcrypt_sha256(password)
                user.website = website
                user.affiliation = affiliation
                user.country = country
                db.session.commit()
                db.session.close()
                return jsonify({'data':['success']})

    @app.route('/admin/team/<teamid>/ban', methods=['POST'])
    @admins_only
    def ban(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        user.banned = 1
        db.session.commit()
        return redirect('/scoreboard')

    @app.route('/admin/team/<teamid>/unban', methods=['POST'])
    @admins_only
    def unban(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        user.banned = None
        db.session.commit()
        return redirect('/scoreboard')

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
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
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

    @app.route('/admin/statistics', methods=['GET'])
    @admins_only
    def admin_stats():
        db.session.commit()
        
        teams_registered = db.session.query(db.func.count(Teams.id)).first()[0]
        site_hits = db.session.query(db.func.count(Tracking.id)).first()[0]
        wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
        solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
        challenge_count = db.session.query(db.func.count(Challenges.id)).first()[0]
        most_solved_chal = Solves.query.add_columns(db.func.count(Solves.chalid).label('solves')).group_by(Solves.chalid).order_by('solves DESC').first()
        least_solved_chal = Solves.query.add_columns(db.func.count(Solves.chalid).label('solves')).group_by(Solves.chalid).order_by('solves ASC').first()

        db.session.close()

        return render_template('admin/statistics.html', team_count=teams_registered,
            hit_count=site_hits, 
            wrong_count=wrong_count, 
            solve_count=solve_count, 
            challenge_count=challenge_count,
            most_solved=most_solved_chal,
            least_solved = least_solved_chal
            )



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

            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], md5hash)):
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], md5hash))

            f.save(os.path.join(app.config['UPLOAD_FOLDER'], md5hash, filename))
            db_f = Files(chal.id, os.path.join(app.config['UPLOAD_FOLDER'], md5hash, filename))
            db.session.add(db_f)

        db.session.commit()
        db.session.close()
        return redirect('/admin/chals')

    @app.route('/admin/chal/update', methods=['POST'])
    def admin_update_chal():
        challenge=Challenges.query.filter_by(id=request.form['id']).first()
        challenge.name = request.form['name']
        challenge.description = request.form['desc']
        challenge.value = request.form['value']
        challenge.category = request.form['category']
        db.session.add(challenge)
        db.session.commit()
        db.session.close()
        return redirect('/admin/chals')
