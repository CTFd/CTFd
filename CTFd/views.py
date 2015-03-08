from flask import current_app as app, render_template, render_template_string, request, redirect, abort, jsonify, json as json_mod, url_for, session
from CTFd.utils import authed, ip2long, long2ip, is_setup
from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config

from jinja2.exceptions import TemplateNotFound
from passlib.hash import bcrypt_sha256
from collections import OrderedDict

import logging
import os
import re
import sys
import json
import os

def init_views(app):
    @app.before_request
    def tracker():
        if authed():
            if not Tracking.query.filter_by(ip=ip2long(request.remote_addr)).first():
                visit = Tracking(request.remote_addr, session['id'])
                db.session.add(visit)
                db.session.commit()
                db.session.close()

    @app.before_request
    def csrf():
        if authed() and request.method == "POST":
            if session['nonce'] != request.form.get('nonce'):
                abort(403)

    @app.before_request
    def redirect_setup():
        if request.path == "/static/css/style.css":
            return
        if not is_setup() and request.path != "/setup":
            return redirect('/setup')

    @app.before_first_request
    def needs_setup():
        if not is_setup():
            return redirect('/setup')

    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        # with app.app_context():
            # admin = Teams.query.filter_by(admin=True).first()

        if not is_setup():
            if request.method == 'POST':
                ## Admin user
                name = request.form['name']
                email = request.form['email']
                password = request.form['password']
                admin = Teams(name, email, password)
                admin.admin = True

                ## Index page
                html = request.form['html']
                page = Pages('index', html)

                ## Start time
                start = Config('start', None)
                end = Config('end', None)

                ## Challenges cannot be viewed by unregistered users
                view_challenges_unregistered = Config('view_challenges_unregistered', None)

                ## Allow/Disallow registration
                prevent_registration = Config('prevent_registration', None)

                setup = Config('setup', True)

                db.session.add(admin)
                db.session.add(page)
                db.session.add(start)
                db.session.add(end)
                db.session.add(view_challenges_unregistered)
                db.session.add(prevent_registration)
                db.session.add(setup)
                db.session.commit()
                app.setup = False
                return redirect('/')
            return render_template('setup.html')
        return redirect('/')

    # Static HTML files
    @app.route("/", defaults={'template': 'index'})
    @app.route("/<template>")
    def static_html(template):
        try:
            return render_template('%s.html' % template)
        except TemplateNotFound:
            page = Pages.query.filter_by(route=template).first()
            if page:
                return render_template_string('{% extends "base.html" %}{% block content %}' + page.html + '{% endblock %}')
            else:
                abort(404)

    @app.route('/teams')
    def teams():
        teams = Teams.query.all()
        return render_template('teams.html', teams=teams)

    @app.route('/team/<teamid>', methods=['GET', 'POST'])
    def team(teamid):
        user = Teams.query.filter_by(id=teamid).first()
        solves = Solves.query.filter_by(teamid=teamid).all()
        score = user.score()
        place = user.place()
        db.session.close()

        if request.method == 'GET':
            return render_template('team.html', solves=solves, team=user, score=score, place=place)
        elif request.method == 'POST':
            json = {'solves':[]}
            for x in solves:
                json['solves'].append({'id':x.id, 'chal':x.chalid, 'team':x.teamid})
            return jsonify(json)


    @app.route('/profile', methods=['POST', 'GET'])
    def profile():
        if authed():
            if request.method == "POST":
                errors = []

                name = request.form.get('name')
                email = request.form.get('email')
                website = request.form.get('website')
                affiliation = request.form.get('affiliation')
                country = request.form.get('country')

                names = Teams.query.filter_by(name=name).first()
                emails = Teams.query.filter_by(email=email).first()
                valid_email = re.match("[^@]+@[^@]+\.[^@]+", email)
                
                name_len = len(request.form['name']) == 0

                if not bcrypt_sha256.verify(request.form.get('confirm').strip(), names.password):
                    errors.append("Your old password doesn't match what we have.")
                if not valid_email:
                    errors.append("That email doesn't look right")
                if names and name!=session['username']: 
                    errors.append('That team name is already taken')
                if emails and emails.id != session['id']:
                    errors.append('That email has already been used')
                if name_len:
                    errors.append('Pick a longer team name')

                if len(errors) > 0:
                    return render_template('profile.html', name=name, email=email, website=website, affiliation=affiliation, country=country, errors=errors)
                else:
                    team = Teams.query.filter_by(id=session['id']).first()
                    team.name = name
                    team.email = email
                    if 'password' in request.form.keys() and not len(request.form['password']) == 0:
                        team.password = bcrypt_sha256.encrypt(request.form.get('password'))
                    team.website = website
                    team.affiliation = affiliation
                    team.country = country
                    db.session.commit()
                    db.session.close()
                    return redirect('/profile')
            else:
                user = Teams.query.filter_by(id=session['id']).first()
                name = user.name
                email = user.email
                website = user.website
                affiliation = user.affiliation
                country = user.country
                return render_template('profile.html', name=name, email=email, website=website, affiliation=affiliation, country=country)
        else:
            return redirect('/login')
