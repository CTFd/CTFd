from flask import (
    current_app as app,
    render_template,
    request,
    redirect,
    url_for,
    session,
    Blueprint,
)
from CTFd.models import db, Users, Teams

from CTFd.utils import get_config, get_app_config
from CTFd.utils.decorators import ratelimit
from CTFd.utils import user as current_user
from CTFd.utils import config, validators
from CTFd.utils import email
from CTFd.utils.security.auth import login_user, logout_user
from CTFd.utils.security.passwords import hash_password, check_password
from CTFd.utils.logging import log
from CTFd.utils.decorators.visibility import check_registration_visibility
from CTFd.utils.modes import TEAMS_MODE, USERS_MODE
from CTFd.utils.security.signing import serialize, unserialize, SignatureExpired, BadSignature, BadTimeSignature
from CTFd.utils.helpers import info_for, error_for, get_errors, get_infos
from CTFd.utils.config.visibility import registration_visible

import base64
import requests

auth = Blueprint('auth', __name__)


@auth.route('/confirm', methods=['POST', 'GET'])
@auth.route('/confirm/<data>', methods=['GET'])
@ratelimit(method="POST", limit=10, interval=60)
def confirm(data=None):
    if not get_config('verify_emails'):
        # If the CTF doesn't care about confirming email addresses then redierct to challenges
        return redirect(url_for('challenges.listing'))

    # User is confirming email account
    if data and request.method == "GET":
        try:
            user_email = unserialize(data, max_age=1800)
        except (BadTimeSignature, SignatureExpired):
            return render_template('confirm.html', errors=['Your confirmation link has expired'])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('confirm.html', errors=['Your confirmation token is invalid'])

        user = Users.query.filter_by(email=user_email).first_or_404()
        user.verified = True
        log('registrations', format="[{date}] {ip} -  successful password reset for {name}")
        db.session.commit()
        db.session.close()
        if current_user.authed():
            return redirect(url_for('challenges.listing'))
        return redirect(url_for('auth.login'))

    # User is trying to start or restart the confirmation flow
    if not current_user.authed():
        return redirect(url_for('auth.login'))

    user = Users.query.filter_by(id=session['id']).first_or_404()
    if user.verified:
        return redirect(url_for('views.settings'))

    if data is None:
        if request.method == "POST":
            # User wants to resend their confirmation email
            email.verify_email_address(user.email)
            log('registrations', format="[{date}] {ip} - {name} initiated a confirmation email resend")
            return render_template('confirm.html', user=user, infos=['Your confirmation email has been resent!'])
        elif request.method == "GET":
            # User has been directed to the confirm page
            return render_template('confirm.html', user=user)


@auth.route('/reset_password', methods=['POST', 'GET'])
@auth.route('/reset_password/<data>', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=60)
def reset_password(data=None):
    if data is not None:
        try:
            name = unserialize(data, max_age=1800)
        except (BadTimeSignature, SignatureExpired):
            return render_template('reset_password.html', errors=['Your link has expired'])
        except (BadSignature, TypeError, base64.binascii.Error):
            return render_template('reset_password.html', errors=['Your reset token is invalid'])

        if request.method == "GET":
            return render_template('reset_password.html', mode='set')
        if request.method == "POST":
            user = Users.query.filter_by(name=name).first_or_404()
            user.password = request.form['password'].strip()
            db.session.commit()
            log('logins', format="[{date}] {ip} -  successful password reset for {name}", name=name)
            db.session.close()
            return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email_address = request.form['email'].strip()
        team = Users.query.filter_by(email=email_address).first()

        errors = get_errors()

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

        email.forgot_password(email_address, team.name)

        return render_template(
            'reset_password.html',
            errors=['If that account exists you will receive an email, please check your inbox']
        )
    return render_template('reset_password.html')


@auth.route('/register', methods=['POST', 'GET'])
@check_registration_visibility
@ratelimit(method="POST", limit=10, interval=5)
def register():
    errors = get_errors()
    if request.method == 'POST':
        name = request.form['name']
        email_address = request.form['email']
        password = request.form['password']

        name_len = len(name) == 0
        names = Users.query.add_columns('name', 'id').filter_by(name=name).first()
        emails = Users.query.add_columns('email', 'id').filter_by(email=email_address).first()
        pass_short = len(password) == 0
        pass_long = len(password) > 128
        valid_email = validators.validate_email(request.form['email'])
        team_name_email_check = validators.validate_email(name)

        if not valid_email:
            errors.append("Please enter a valid email address")
        if email.check_email_is_whitelisted(email_address) is False:
                errors.append(
                    "Only email addresses under {domains} may register".format(
                        domains=get_config('domain_whitelist')
                    )
                )
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
            return render_template(
                'register.html',
                errors=errors,
                name=request.form['name'],
                email=request.form['email'],
                password=request.form['password']
            )
        else:
            with app.app_context():
                user = Users(
                    name=name.strip(),
                    email=email_address.lower(),
                    password=password.strip()
                )
                db.session.add(user)
                db.session.commit()
                db.session.flush()

                login_user(user)

                if config.can_send_mail() and get_config('verify_emails'):  # Confirming users is enabled and we can send email.
                    log('registrations', format="[{date}] {ip} - {name} registered (UNCONFIRMED) with {email}")
                    email.verify_email_address(user.email)
                    db.session.close()
                    return redirect(url_for('auth.confirm'))
                else:  # Don't care about confirming users
                    if config.can_send_mail():  # We want to notify the user that they have registered.
                        email.sendmail(
                            request.form['email'],
                            "You've successfully registered for {}".format(get_config('ctf_name'))
                        )

        log('registrations', "[{date}] {ip} - {name} registered with {email}")
        db.session.close()
        return redirect(url_for('challenges.listing'))
    else:
        return render_template('register.html', errors=errors)


@auth.route('/login', methods=['POST', 'GET'])
@ratelimit(method="POST", limit=10, interval=5)
def login():
    errors = get_errors()
    if request.method == 'POST':
        name = request.form['name']

        # Check if the user submitted an email address or a team name
        if validators.validate_email(name) is True:
            user = Users.query.filter_by(email=name).first()
        else:
            user = Users.query.filter_by(name=name).first()

        if user:
            if user and check_password(request.form['password'], user.password):
                session.regenerate()

                login_user(user)
                log('logins', "[{date}] {ip} - {name} logged in")

                db.session.close()
                if request.args.get('next') and validators.is_safe_url(request.args.get('next')):
                    return redirect(request.args.get('next'))
                return redirect(url_for('challenges.listing'))

            else:
                # This user exists but the password is wrong
                log('logins', "[{date}] {ip} - submitted invalid password for {name}")
                errors.append("Your username or password is incorrect")
                db.session.close()
                return render_template('login.html', errors=errors)
        else:
            # This user just doesn't exist
            log('logins', "[{date}] {ip} - submitted invalid account information")
            errors.append("Your username or password is incorrect")
            db.session.close()
            return render_template('login.html', errors=errors)
    else:
        db.session.close()
        return render_template('login.html', errors=errors)


@auth.route('/oauth')
def oauth_login():
    endpoint = get_app_config('OAUTH_AUTHORIZATION_ENDPOINT') \
        or get_config('oauth_authorization_endpoint') \
        or 'https://auth.majorleaguecyber.org/oauth/authorize'

    if get_config('user_mode') == 'teams':
        scope = 'profile team'
    else:
        scope = 'profile'

    client_id = get_app_config('OAUTH_CLIENT_ID') or get_config('oauth_client_id')

    if client_id is None:
        error_for(
            endpoint='auth.login',
            message='OAuth Settings not configured. '
                    'Ask your CTF administrator to configure MajorLeagueCyber integration.'
        )
        return redirect(url_for('auth.login'))

    redirect_url = "{endpoint}?response_type=code&client_id={client_id}&scope={scope}&state={state}".format(
        endpoint=endpoint,
        client_id=client_id,
        scope=scope,
        state=session['nonce']
    )
    return redirect(redirect_url)


@auth.route('/redirect', methods=['GET'])
@ratelimit(method="GET", limit=10, interval=60)
def oauth_redirect():
    oauth_code = request.args.get('code')
    state = request.args.get('state')
    if session['nonce'] != state:
        log('logins', "[{date}] {ip} - OAuth State validation mismatch")
        error_for(endpoint='auth.login', message='OAuth State validation mismatch.')
        return redirect(url_for('auth.login'))

    if oauth_code:
        url = get_app_config('OAUTH_TOKEN_ENDPOINT') \
            or get_config('oauth_token_endpoint') \
            or 'https://auth.majorleaguecyber.org/oauth/token'

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
            user_url = get_app_config('OAUTH_API_ENDPOINT') \
                or get_config('oauth_api_endpoint') \
                or 'https://api.majorleaguecyber.org/user'

            headers = {
                'Authorization': 'Bearer ' + str(token),
                'Content-type': 'application/json'
            }
            api_data = requests.get(url=user_url, headers=headers).json()

            user_id = api_data['id']
            user_name = api_data['name']
            user_email = api_data['email']

            user = Users.query.filter_by(email=user_email).first()
            if user is None:
                # Check if we are allowing registration before creating users
                if registration_visible():
                    user = Users(
                        name=user_name,
                        email=user_email,
                        oauth_id=user_id,
                        verified=True
                    )
                    db.session.add(user)
                    db.session.commit()
                else:
                    log('logins', "[{date}] {ip} - Public registration via MLC blocked")
                    error_for(
                        endpoint='auth.login',
                        message='Public registration is disabled. Please try again later.'
                    )
                    return redirect(url_for('auth.login'))

            if get_config('user_mode') == TEAMS_MODE:
                team_id = api_data['team']['id']
                team_name = api_data['team']['name']

                team = Teams.query.filter_by(oauth_id=team_id).first()
                if team is None:
                    team = Teams(
                        name=team_name,
                        oauth_id=team_id
                    )
                    db.session.add(team)
                    db.session.commit()

                team.members.append(user)
                db.session.commit()

            if user.oauth_id is None:
                user.oauth_id = user_id
                user.verified = True
                db.session.commit()

            login_user(user)

            return redirect(url_for('challenges.listing'))
        else:
            log('logins', "[{date}] {ip} - OAuth token retrieval failure")
            error_for(
                endpoint='auth.login',
                message='OAuth token retrieval failure.'
            )
            return redirect(url_for('auth.login'))
    else:
        log('logins', "[{date}] {ip} - Received redirect without OAuth code")
        error_for(
            endpoint='auth.login',
            message='Received redirect without OAuth code.'
        )
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    if current_user.authed():
        logout_user()
    return redirect(url_for('views.static_html'))
