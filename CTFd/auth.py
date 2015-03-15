from flask import render_template, request, redirect, abort, jsonify, url_for, session
from CTFd.utils import sha512, is_safe_url, authed, mailserver, sendmail, can_register
from CTFd.models import db, Teams

from itsdangerous import TimedSerializer, BadTimeSignature
from passlib.hash import bcrypt_sha256
from flask import current_app as app

import logging
import time
import re
import os

def init_auth(app):
    @app.context_processor
    def inject_user():
        if authed():
            return dict(session)
        return dict()

    @app.route('/reset_password', methods=['POST', 'GET'])
    @app.route('/reset_password/<data>', methods=['POST', 'GET'])
    def reset_password(data=None):
        if data is not None and request.method == "GET":
            return render_template('reset_password.html', mode='set')
        if data is not None and request.method == "POST":
            try:
                s = TimedSerializer(app.config['SECRET_KEY'])
                name = s.loads(data.decode('base64'), max_age=1800)
            except BadTimeSignature:
                return render_template('reset_password.html', errors=['Your link has expired'])
            team = Teams.query.filter_by(name=name).first()
            team.password = sha512(request.form['password'].strip())
            db.session.commit()
            db.session.close()
            return redirect('/login')

        if request.method == 'POST':
            email = request.form['email'].strip()
            team = Teams.query.filter_by(email=email).first()
            if not team:
                return render_template('reset_password.html', errors=['Check your email'])
            s = TimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(team.name)
            text = """
Did you initiate a password reset? 

{0}/reset_password/{1}

    """.format(app.config['HOST'], token.encode('base64'))

            sendmail(email, text)

            return render_template('reset_password.html', errors=['Check your email'])
        return render_template('reset_password.html')

    @app.route('/register', methods=['POST', 'GET'])
    def register():
        if not can_register():
            return redirect('/login')
        if request.method == 'POST':
            errors = []
            name_len = len(request.form['name']) == 0
            names = Teams.query.add_columns('name', 'id').filter_by(name=request.form['name']).first()
            emails = Teams.query.add_columns('email', 'id').filter_by(email=request.form['email']).first()
            pass_short = len(request.form['password']) == 0
            pass_long = len(request.form['password']) > 128
            valid_email = re.match("[^@]+@[^@]+\.[^@]+", request.form['email'])

            if not valid_email:
                errors.append("That email doesn't look right")
            if names: 
                errors.append('That team name is already taken')
            if emails:
                errors.append('That email has already been used')
            if pass_short:
                errors.append('Pick a longer password')
            if pass_long:
                errors.append('Pick a shorter password')
            if name_len:
                errors.append('Pick a longer team name')

            if len(errors) > 0:
                return render_template('register.html', errors=errors, name=request.form['name'], email=request.form['email'], password=request.form['password'])
            else:
                with app.app_context():
                    team = Teams(request.form['name'], request.form['email'], request.form['password'])
                    db.session.add(team)
                    db.session.commit()
                if mailserver():
                    sendmail(request.form['email'], "You've successfully registered for the CTF")
            
            db.session.close()

            logger = logging.getLogger('regs')
            logger.warn("[{0}] {1} registered with {2}".format(time.strftime("%m/%d/%Y %X"), request.form['name'].encode('utf-8'), request.form['email'].encode('utf-8')))
            return redirect('/login')
        else:
            return render_template('register.html')

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == 'POST':
            errors = []
            # team = Teams.query.filter_by(name=request.form['name'], password=sha512(request.form['password'])).first()
            team = Teams.query.filter_by(name=request.form['name']).first()
            if team and bcrypt_sha256.verify(request.form['password'], team.password):
                try:
                    session.regenerate() # NO SESSION FIXATION FOR YOU
                except:
                    pass # TODO: Some session objects don't implement regenerate :(
                session['username'] = team.name
                session['id'] = team.id
                session['admin'] = team.admin
                session['nonce'] = sha512(os.urandom(10))
                db.session.close()

                logger = logging.getLogger('logins')
                logger.warn("[{0}] {1} logged in".format(time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8')))    

                # if request.args.get('next') and is_safe_url(request.args.get('next')):
                #     return redirect(request.args.get('next'))
                return redirect('/team/{0}'.format(team.id))
            else:
                errors.append("That account doesn't seem to exist")
                db.session.close()
                return render_template('login.html', errors=errors)
        else:
            db.session.close()
            return render_template('login.html')


    @app.route('/logout')
    def logout():
        if authed():
            session.clear()
        return redirect('/')
