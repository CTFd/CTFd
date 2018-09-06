from flask import current_app as app, render_template, request, redirect, url_for, session, Blueprint, abort
from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Users, Teams

from CTFd.utils import get_config, get_app_config
from CTFd.utils.encoding import base64encode, base64decode
from CTFd.utils.decorators import ratelimit
from CTFd.utils import user as current_user
from CTFd.utils import config, validators, email
from CTFd.utils.security.csrf import generate_nonce

import base64
import logging
import requests
import time

auth = Blueprint('auth', __name__)


@auth.route('/confirm', methods=['POST', 'GET'])
@auth.route('/confirm/<data>', methods=['GET'])
@ratelimit(method="POST", limit=10, interval=60)
def confirm(data=None):
    if not get_config('verify_emails'):
        # If the CTF doesn't care about confirming email addresses then redierct to challenges
        return redirect(url_for('challenges.challenges_view'))

    logger = logging.getLogger('regs')
    # User is confirming email account
    if data and request.method == "GET":
        try:
            s = TimedSerializer(app.config['SECRET_KEY'])
            user_email = s.loads(base64decode(data), max_age=1800)
        except BadTimeSignature:
            return render_template('confirm.html', errors=['Your confirmation link has expired'])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('confirm.html', errors=['Your confirmation token is invalid'])
        team = Users.query.filter_by(email=user_email).first_or_404()
        team.verified = True
        db.session.commit()
        logger.warn("[{date}] {ip} - {username} confirmed their account".format(
            date=time.strftime("%m/%d/%Y %X"),
            ip=current_user.get_ip(),
            username=team.name.encode('utf-8'),
            email=team.email.encode('utf-8')
        ))
        db.session.close()
        if current_user.authed():
            return redirect(url_for('challenges.challenges_view'))
        return redirect(url_for('auth.login'))

    # User is trying to start or restart the confirmation flow
    if not current_user.authed():
        return redirect(url_for('auth.login'))

    team = Users.query.filter_by(id=session['id']).first_or_404()

    if data is None:
        if request.method == "POST":
            # User wants to resend their confirmation email
            if team.verified:
                return redirect(url_for('views.profile'))
            else:
                email.verify_email_address(team.email)
                logger.warn("[{date}] {ip} - {username} initiated a confirmation email resend".format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=current_user.get_ip(),
                    username=team.name.encode('utf-8'),
                    email=team.email.encode('utf-8')
                ))
            return render_template('confirm.html', team=team, infos=['Your confirmation email has been resent!'])
        elif request.method == "GET":
            # User has been directed to the confirm page
            team = Users.query.filter_by(id=session['id']).first_or_404()
            if team.verified:
                # If user is already verified, redirect to their profile
                return redirect(url_for('views.profile'))
            return render_template('confirm.html', team=team)


# TODO: Maybe consider renaming this to just /reset. Includes the function name as well
@auth.route('/reset_password', methods=['POST', 'GET'])
@auth.route('/reset_password/<data>', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=60)
def reset_password(data=None):
    logger = logging.getLogger('logins')

    if data is not None:
        try:
            s = TimedSerializer(app.config['SECRET_KEY'])
            name = s.loads(base64decode(data), max_age=1800)
        except BadTimeSignature:
            return render_template('reset_password.html', errors=['Your link has expired'])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('reset_password.html', errors=['Your reset token is invalid'])

        if request.method == "GET":
            return render_template('reset_password.html', mode='set')
        if request.method == "POST":
            team = Users.query.filter_by(name=name).first_or_404()
            team.password = bcrypt_sha256.encrypt(request.form['password'].strip())
            db.session.commit()
            logger.warn("[{date}] {ip} -  successful password reset for {username}".format(
                date=time.strftime("%m/%d/%Y %X"),
                ip=current_user.get_ip(),
                username=team.name.encode('utf-8')
            ))
            db.session.close()
            return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form['email'].strip()
        team = Users.query.filter_by(email=email).first()

        errors = []

        if config.can_send_mail() is False:
            return render_template(
                'reset_password.html',
                errors=['Email could not be sent due to server misconfiguration']
            )

        if not team:
            return render_template(
                'reset_password.html',
                errors=['If that account exists you will receive an email, please check your inbox']
            )

        email.forgot_password(email, team.name)

        return render_template(
            'reset_password.html',
            errors=['If that account exists you will receive an email, please check your inbox']
        )
    return render_template('reset_password.html')


@auth.route('/register', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=5)
def register():
    logger = logging.getLogger('regs')
    if not config.can_register():
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        errors = []
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        name_len = len(name) == 0
        names = Users.query.add_columns('name', 'id').filter_by(name=name).first()
        emails = Users.query.add_columns('email', 'id').filter_by(email=email).first()
        pass_short = len(password) == 0
        pass_long = len(password) > 128
        valid_email = validators.validate_email(request.form['email'])
        team_name_email_check = validators.validate_email(name)

        if not valid_email:
            errors.append("Please enter a valid email address")
        if names:
            errors.append('That team name is already taken')
        if team_name_email_check is True:
            errors.append('Your team name cannot be an email address')
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
                user = Users(
                    name=name.strip(),
                    email=email.lower(),
                    password=password.strip()
                )
                db.session.add(user)
                db.session.commit()
                db.session.flush()

                session['username'] = user.name
                session['id'] = user.id
                session['admin'] = user.admin
                session['nonce'] = generate_nonce()

                if config.can_send_mail() and get_config('verify_emails'):  # Confirming users is enabled and we can send email.
                    logger = logging.getLogger('regs')
                    logger.warn("[{date}] {ip} - {username} registered (UNCONFIRMED) with {email}".format(
                        date=time.strftime("%m/%d/%Y %X"),
                        ip=current_user.get_ip(),
                        username=request.form['name'].encode('utf-8'),
                        email=request.form['email'].encode('utf-8')
                    ))
                    email.verify_email_address(user.email)
                    db.session.close()
                    return redirect(url_for('auth.confirm'))
                else:  # Don't care about confirming users
                    if config.can_send_mail():  # We want to notify the user that they have registered.
                        email.sendmail(request.form['email'], "You've successfully registered for {}".format(get_config('ctf_name')))

        logger.warn("[{date}] {ip} - {username} registered with {email}".format(
            date=time.strftime("%m/%d/%Y %X"),
            ip=current_user.get_ip(),
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
        if validators.validate_email(name) is True:
            user = Users.query.filter_by(email=name).first()
        else:
            user = Users.query.filter_by(name=name).first()

        if user:
            if user and bcrypt_sha256.verify(request.form['password'], user.password):
                try:
                    session.regenerate()  # NO SESSION FIXATION FOR YOU
                except:
                    pass  # TODO: Some session objects don't implement regenerate :(
                session['username'] = user.name
                session['id'] = user.id
                session['admin'] = user.admin
                session['nonce'] = generate_nonce()
                db.session.close()

                logger.warn("[{date}] {ip} - {username} logged in".format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=current_user.get_ip(),
                    username=session['username'].encode('utf-8')
                ))

                if request.args.get('next') and validators.is_safe_url(request.args.get('next')):
                    return redirect(request.args.get('next'))
                return redirect(url_for('challenges.challenges_view'))

            else:  # This user exists but the password is wrong
                logger.warn("[{date}] {ip} - submitted invalid password for {username}".format(
                    date=time.strftime("%m/%d/%Y %X"),
                    ip=current_user.get_ip(),
                    username=user.name.encode('utf-8')
                ))
                errors.append("Your username or password is incorrect")
                db.session.close()
                return render_template('login.html', errors=errors)

        else:  # This user just doesn't exist
            logger.warn("[{date}] {ip} - submitted invalid account information".format(
                date=time.strftime("%m/%d/%Y %X"),
                ip=current_user.get_ip()
            ))
            errors.append("Your username or password is incorrect")
            db.session.close()
            return render_template('login.html', errors=errors)

    else:
        db.session.close()
        return render_template('login.html')


@auth.route('/oauth', methods=['GET', 'POST'])
def oauth_login():
    endpoint = get_app_config('OAUTH_AUTHORIZATION_ENDPOINT') or get_config('oauth_authorization_endpoint')

    client_id = get_app_config('OAUTH_CLIENT_ID') or get_config('oauth_client_id')
    redirect_url = "{endpoint}?response_type=code&client_id={client_id}".format(
        endpoint=endpoint,
        client_id=client_id
    )
    return redirect(redirect_url)


@auth.route('/redirect', methods=['GET'])
def oauth_redirect():
    oauth_code = request.args.get('code')
    if oauth_code:
        url = get_app_config('OAUTH_TOKEN_ENDPOINT') or get_config('oauth_token_endpoint')
        client_id = get_app_config('OAUTH_CLIENT_ID') or get_config('oauth_client_id')
        client_secret = get_app_config('OAUTH_CLIENT_SECRET') or get_config('oauth_client_secret')
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        data = {
            'code': oauth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code'
        }
        token_request = requests.post(url, data=data, headers=headers)

        if token_request.status_code == requests.codes.ok:
            token = token_request.json()['access_token']
            user_url = get_app_config('OAUTH_API_ENDPOINT') or get_config('oauth_api_endpoint')
            headers = {
                'Authorization': 'Bearer ' + str(token),
                'Content-type': 'application/json'
            }
            api_data = requests.get(url=user_url, headers=headers).json()

            user_id = api_data['id']
            user_name = api_data['name']
            user_email = api_data['email']

            team_id = api_data['team']['id']
            team_name = api_data['team']['name']

            user = Users.query.filter_by(email=user_email).first()
            if user is None:
                user = Users(
                    name=user_name,
                    email=user_email,
                    oauth_id=user_id
                )
                db.session.add(user)
                db.session.commit()

            team = Teams.query.filter_by(oauth_id=team_id).first()
            if team is None:
                team = Teams(
                    name=team_name
                )
                db.session.add(team)
                db.session.commit()

            team.members.append(user)

            session['id'] = user.id
            session['username'] = user.name
            session['email'] = user.email
            session['admin'] = user.admin
            session['nonce'] = generate_nonce()

            return redirect(url_for('challenges.challenges_view'))
    else:
        # TODO: Change this to redirect back to login with an error
        abort(500)


@auth.route('/logout')
def logout():
    if current_user.authed():
        session.clear()
    return redirect(url_for('views.static_html'))
