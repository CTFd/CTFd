from flask import current_app as app, render_template, render_template_string, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint, Response
from CTFd.utils import authed, ip2long, long2ip, is_setup, validate_url, get_config, sha512
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

views = Blueprint('views', __name__)


@views.before_request
def tracker():
    if authed():
        if not Tracking.query.filter_by(ip=ip2long(request.remote_addr)).first():
            visit = Tracking(request.remote_addr, session['id'])
            db.session.add(visit)
            db.session.commit()
            db.session.close()


@views.before_request
def csrf():
    if request.method == "POST":
        print(session)
        print(request.form.get('nonce'))
        if session['nonce'] != request.form.get('nonce'):
            abort(403)


@views.before_request
def redirect_setup():
    if request.path == "/static/css/style.css":
        return
    if not is_setup() and request.path != "/setup":
        return redirect('/setup')


@views.route('/setup', methods=['GET', 'POST'])
def setup():
    # with app.app_context():
        # admin = Teams.query.filter_by(admin=True).first()

    if not is_setup():
        if not session.get('nonce'):
            session['nonce'] = sha512(os.urandom(10))
        if request.method == 'POST':
            ctf_name = request.form['ctf_name']
            ctf_name = Config('ctf_name', ctf_name)

            ## CSS
            css = Config('start', '')

            ## Admin user
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            admin = Teams(name, email, password)
            admin.admin = True
            admin.banned = True

            ## Index page
            html = request.form['html']
            page = Pages('index', html)

            #max attempts per challenge
            max_tries = Config("max_tries",0)


            ## Start time
            start = Config('start', None)
            end = Config('end', None)

            ## Challenges cannot be viewed by unregistered users
            view_challenges_unregistered = Config('view_challenges_unregistered', None)

            ## Allow/Disallow registration
            prevent_registration = Config('prevent_registration', None)

            setup = Config('setup', True)

            db.session.add(ctf_name)
            db.session.add(admin)
            db.session.add(page)
            db.session.add(max_tries)
            db.session.add(start)
            db.session.add(end)
            db.session.add(view_challenges_unregistered)
            db.session.add(prevent_registration)
            db.session.add(css)
            db.session.add(setup)
            db.session.commit()
            app.setup = False
            return redirect('/')
        print(session.get('nonce'))
        return render_template('setup.html', nonce=session.get('nonce'))
    return redirect('/')


# Custom CSS handler
@views.route('/static/user.css')
def custom_css():
    return Response(get_config("css"), mimetype='text/css')


# Static HTML files
@views.route("/", defaults={'template': 'index'})
@views.route("/<template>")
def static_html(template):
    try:
        return render_template('%s.html' % template)
    except TemplateNotFound:
        page = Pages.query.filter_by(route=template).first()
        if page:
            return render_template_string('{% extends "base.html" %}{% block content %}' + page.html + '{% endblock %}')
        else:
            abort(404)


@views.route('/teams', defaults={'page':'1'})
@views.route('/teams/<page>')
def teams(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * ( page - 1 )
    page_end = results_per_page * ( page - 1 ) + results_per_page

    teams = Teams.query.slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Teams.id)).first()[0]
    print(count)
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('teams.html', teams=teams, team_pages=pages)

@views.route('/team/<teamid>', methods=['GET', 'POST'])
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


@views.route('/profile', methods=['POST', 'GET'])
def profile():
    if authed():
        if request.method == "POST":
            errors = []

            name = request.form.get('name')
            email = request.form.get('email')
            website = request.form.get('website')
            affiliation = request.form.get('affiliation')
            country = request.form.get('country')

            user = Teams.query.filter_by(id=session['id']).first()

            if not get_config('prevent_name_change'):
                names = Teams.query.filter_by(name=name).first()
                name_len = len(request.form['name']) == 0

            emails = Teams.query.filter_by(email=email).first()
            valid_email = re.match("[^@]+@[^@]+\.[^@]+", email)

            if ('password' in request.form.keys() and not len(request.form['password']) == 0) and \
                    (not bcrypt_sha256.verify(request.form.get('confirm').strip(), user.password)):
                errors.append("Your old password doesn't match what we have.")
            if not valid_email:
                errors.append("That email doesn't look right")
            if not get_config('prevent_name_change') and names and name!=session['username']:
                errors.append('That team name is already taken')
            if emails and emails.id != session['id']:
                errors.append('That email has already been used')
            if not get_config('prevent_name_change') and name_len:
                errors.append('Pick a longer team name')
            if website.strip() and not validate_url(website):
                errors.append("That doesn't look like a valid URL")

            if len(errors) > 0:
                return render_template('profile.html', name=name, email=email, website=website,
                                       affiliation=affiliation, country=country, errors=errors)
            else:
                team = Teams.query.filter_by(id=session['id']).first()
                if not get_config('prevent_name_change'):
                    team.name = name
                team.email = email
                session['username'] = team.name

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
            prevent_name_change = get_config('prevent_name_change')
            return render_template('profile.html', name=name, email=email, website=website, affiliation=affiliation,
                                   country=country, prevent_name_change=prevent_name_change)
    else:
        return redirect('/login')
