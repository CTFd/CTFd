import logging
import os
import re
import time

from flask import current_app as app, render_template, request, redirect, url_for, session, Blueprint
from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Teams
from CTFd import utils
from CTFd.utils import ratelimit, get_tip

import base64

auth = Blueprint('auth', __name__)


@auth.route('/confirm', methods=['POST', 'GET'])
@auth.route('/confirm/<data>', methods=['GET'])
@ratelimit(method="POST", limit=10, interval=60)
def confirm_user(data=None):
    if not utils.get_config('verify_emails'):
        # If the CTF doesn't care about confirming email addresses then redierct to challenges
        return redirect(url_for('challenges.challenges_view'))

    logger = logging.getLogger('regs')
    # User is confirming email account
    if data and request.method == "GET":
        try:
            s = TimedSerializer(app.config['SECRET_KEY'])
            email = s.loads(utils.base64decode(data, urldecode=True), max_age=1800)
        except BadTimeSignature:
            return render_template('confirm.html', errors=[get_tip('LINK_EXPIRED')])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('confirm.html', errors=[get_tip('INVIDE_RESET_TOKEN')])
        team = Teams.query.filter_by(email=email).first_or_404()
        team.verified = True
        db.session.commit()
        logger.warn(get_tip('USER_HAVE_CM').format(
            date=time.strftime("%m/%d/%Y %X"),
            ip=utils.get_ip(),
            username=team.name.encode('utf-8'),
            email=team.email.encode('utf-8')
        ))
        db.session.close()
        if utils.authed():
            return redirect(url_for('challenges.challenges_view'))
        return redirect(url_for('auth.login'))

    # User is trying to start or restart the confirmation flow
    if not utils.authed():
        return redirect(url_for('auth.login'))

    team = Teams.query.filter_by(id=session['id']).first_or_404()

    if data is None:
        if request.method == "POST":
            # User wants to resend their confirmation email
            if team.verified:
                return redirect(url_for('views.profile'))
            else:
                utils.verify_email(team.email)
                logger.warn(get_tip('EMAIL_CF_RESENT').format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=utils.get_ip(),
                    username=team.name.encode('utf-8'),
                    email=team.email.encode('utf-8')
                ))
            return render_template('confirm.html', team=team, infos=[get_tip('EMAIL_CF_SENT')])
        elif request.method == "GET":
            # User has been directed to the confirm page
            team = Teams.query.filter_by(id=session['id']).first_or_404()
            if team.verified:
                # If user is already verified, redirect to their profile
                return redirect(url_for('views.profile'))
            return render_template('confirm.html', team=team)


@auth.route('/reset_password', methods=['POST', 'GET'])
@auth.route('/reset_password/<data>', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=60)
def reset_password(data=None):
    logger = logging.getLogger('logins')

    if data is not None:
        try:
            s = TimedSerializer(app.config['SECRET_KEY'])
            name = s.loads(utils.base64decode(data, urldecode=True), max_age=1800)
        except BadTimeSignature:
            return render_template('reset_password.html', errors=[get_tip('LINK_EXPIRED')])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('reset_password.html', errors=[get_tip('INVIDE_RESET_TOKEN')])

        if request.method == "GET":
            return render_template('reset_password.html', mode='set')
        if request.method == "POST":
            team = Teams.query.filter_by(name=name).first_or_404()
            team.password = bcrypt_sha256.encrypt(request.form['password'].strip())
            db.session.commit()
            logger.warn(get_tip('PASS_HAVE_RESET').format(
                date=time.strftime("%m/%d/%Y %X"),
                ip=utils.get_ip(),
                username=team.name.encode('utf-8')
            ))
            db.session.close()
            return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        team = Teams.query.filter_by(email=email).first()

        errors = []

        if utils.can_send_mail() is False:
            return render_template(
                'reset_password.html',
                errors=[get_tip('EMAIL_NOT_CONFIG')]
            )

        if not team:
            return render_template(
                'reset_password.html',
                errors=[get_tip('FORGOT_PASS_NOTICE')]
            )

        utils.forgot_password(email, team.name)

        return render_template(
            'reset_password.html',
            errors=[get_tip('FORGOT_PASS_NOTICE')]
        )
    return render_template('reset_password.html')


@auth.route('/register', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=5)
def register():
    logger = logging.getLogger('regs')
    if not utils.can_register():
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        errors = []
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        name_len = len(name) == 0
        names = Teams.query.add_columns('name', 'id').filter_by(name=name).first()
        emails = Teams.query.add_columns('email', 'id').filter_by(email=email).first()
        pass_short = len(password) == 0
        pass_long = len(password) > 128
        valid_email = utils.check_email_format(request.form['email'])
        team_name_email_check = utils.check_email_format(name)

        if not valid_email:
            errors.append(get_tip('INVIDE_EMAIL'))
        if names:
            errors.append(get_tip('TEAM_EXIST'))
        if team_name_email_check is True:
            errors.append(get_tip('EMAIL_NOT_TEAM'))
        if emails:
            errors.append(get_tip('EMAIL_HAVE_USE'))
        if pass_short:
            errors.append(get_tip('TOO_SHORT_PASS'))
        if pass_long:
            errors.append(get_tip('TOO_LONG_PASS'))
        if name_len:
            errors.append(get_tip('TOO_SHORT_TEAM'))

        if len(errors) > 0:
            return render_template('register.html', errors=errors, name=request.form['name'], email=request.form['email'], password=request.form['password'])
        else:
            with app.app_context():
                token = os.urandom(16).encode('hex')
                team = Teams(name, email.lower(), password, token.lower())
                db.session.add(team)
                db.session.commit()
                db.session.flush()

                session['username'] = team.name
                session['id'] = team.id
                session['admin'] = team.admin
                session['nonce'] = utils.sha512(os.urandom(10))

                if utils.can_send_mail() and utils.get_config('verify_emails'):  # Confirming users is enabled and we can send email.
                    logger = logging.getLogger('regs')
                    logger.warn(get_tip('USER_REG_WARN').format(
                        date=time.strftime("%m/%d/%Y %X"),
                        ip=utils.get_ip(),
                        username=request.form['name'].encode('utf-8'),
                        email=request.form['email'].encode('utf-8')
                    ))
                    utils.verify_email(team.email)
                    db.session.close()
                    return redirect(url_for('auth.confirm_user'))
                else:  # Don't care about confirming users
                    if utils.can_send_mail():  # We want to notify the user that they have registered.
                        utils.sendmail(request.form['email'], get_tip('USER_REG_SUCCESS').format(utils.get_config('ctf_name')))

        logger.warn(get_tip('USER_REGISTRED').format(
            date=time.strftime("%m/%d/%Y %X"),
            ip=utils.get_ip(),
            username=request.form['name'].encode('utf-8'),
            email=request.form['email'].encode('utf-8')
        ))
        db.session.close()
        return redirect(url_for('challenges.challenges_view'))
    else:
        return render_template('register.html')


@auth.route('/login', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=5)
def login():
    logger = logging.getLogger('logins')
    if request.method == 'POST':
        errors = []
        name = request.form['name']

        # Check if the user submitted an email address or a team name
        if utils.check_email_format(name) is True:
            team = Teams.query.filter_by(email=name).first()
        else:
            team = Teams.query.filter_by(name=name).first()

        if team:
            if team and bcrypt_sha256.verify(request.form['password'], team.password):
                try:
                    session.regenerate()  # NO SESSION FIXATION FOR YOU
                except:
                    pass  # TODO: Some session objects don't implement regenerate :(
                session['username'] = team.name
                session['id'] = team.id
                session['admin'] = team.admin
                session['nonce'] = utils.sha512(os.urandom(10))
                db.session.close()

                logger.warn(get_tip('USER_LOGINED').format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=utils.get_ip(),
                    username=session['username'].encode('utf-8')
                ))

                if request.args.get('next') and utils.is_safe_url(request.args.get('next')):
                    return redirect(request.args.get('next'))
                return redirect(url_for('challenges.challenges_view'))

            else:  # This user exists but the password is wrong
                logger.warn(get_tip('INVIDE_PASS').format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=utils.get_ip(),
                    username=team.name.encode('utf-8')
                ))
                errors.append(get_tip('INVIDE_USER_PASS'))
                db.session.close()
                return render_template('login.html', errors=errors)

        else:  # This user just doesn't exist
            logger.warn(get_tip('INVIDE_USER').format(
                date=time.strftime("%m/%d/%Y %X"),
                ip=utils.get_ip()
            ))
            errors.append(get_tip('INVIDE_USER_PASS'))
            db.session.close()
            return render_template('login.html', errors=errors)

    else:
        db.session.close()
        return render_template('login.html')


@auth.route('/logout')
def logout():
    if utils.authed():
        session.clear()
    return redirect(url_for('views.static_html'))
