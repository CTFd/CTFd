from flask import current_app as app, render_template, request, redirect, abort, jsonify, url_for, session, Blueprint, Response, send_file
from flask.helpers import safe_join
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Users, Users, Solves, Awards, Files, Pages, Tracking
from CTFd.utils import cache, markdown
from CTFd.utils import get_config, set_config
from CTFd.utils.user import authed, get_ip
from CTFd.utils import config
from CTFd.utils.config.pages import get_page
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import user as current_user
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, unix_time_to_utc
from CTFd.utils import validators

import os

views = Blueprint('views', __name__)


@views.route('/setup', methods=['GET', 'POST'])
def setup():
    if not config.is_setup():
        if not session.get('nonce'):
            session['nonce'] = generate_nonce()
        if request.method == 'POST':
            ctf_name = request.form['ctf_name']
            ctf_name = set_config('ctf_name', ctf_name)

            # CSS
            css = set_config('start', '')

            # Admin user
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            admin = Users(
                name=name,
                email=email,
                password=password
            )
            admin.admin = True
            admin.banned = True

            user_mode = request.form['user_mode']
            user_mode = set_config('user_mode', user_mode)

            # Index page

            index = """<div class="row">
    <div class="col-md-6 offset-md-3">
        <img class="w-100 mx-auto d-block" style="max-width: 500px;padding: 50px;padding-top: 14vh;" src="themes/core/static/img/logo.png" />
        <h3 class="text-center">
            <p>A cool CTF platform from <a href="https://ctfd.io">ctfd.io</a></p>
            <p>Follow us on social media:</p>
            <a href="https://twitter.com/ctfdio"><i class="fab fa-twitter fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://facebook.com/ctfdio"><i class="fab fa-facebook fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://github.com/ctfd"><i class="fab fa-github fa-2x" aria-hidden="true"></i></a>
        </h3>
        <br>
        <h4 class="text-center">
            <a href="admin">Click here</a> to login and setup your CTF
        </h4>
    </div>
</div>""".format(request.script_root)

            page = Pages(
                title=None,
                route='index',
                html=index,
                draft=False
            )

            # max attempts per challenge
            max_tries = set_config('max_tries', 0)

            # Start time
            start = set_config('start', None)
            end = set_config('end', None)
            freeze = set_config('freeze', None)

            # Challenges cannot be viewed by unregistered users
            view_challenges_unregistered = set_config('view_challenges_unregistered', None)

            # Allow/Disallow registration
            prevent_registration = set_config('prevent_registration', None)

            # Verify emails
            verify_emails = set_config('verify_emails', None)

            mail_server = set_config('mail_server', None)
            mail_port = set_config('mail_port', None)
            mail_tls = set_config('mail_tls', None)
            mail_ssl = set_config('mail_ssl', None)
            mail_username = set_config('mail_username', None)
            mail_password = set_config('mail_password', None)
            mail_useauth = set_config('mail_useauth', None)

            setup = set_config('setup', True)

            db.session.add(page)
            db.session.add(admin)
            db.session.commit()

            session['username'] = admin.name
            session['id'] = admin.id
            session['admin'] = admin.admin
            session['nonce'] = generate_nonce()

            db.session.close()
            app.setup = False
            with app.app_context():
                cache.clear()

            return redirect(url_for('views.static_html'))
        return render_template('setup.html', nonce=session.get('nonce'))
    return redirect(url_for('views.static_html'))


# Custom CSS handler
@views.route('/static/user.css')
@cache.cached(timeout=300)
def custom_css():
    return Response(get_config('css'), mimetype='text/css')


# Static HTML files
@views.route("/", defaults={'template': 'index'})
@views.route("/<path:template>")
def static_html(template):
    page = get_page(template)
    if page is None:
        abort(404)
    else:
        if page.auth_required and authed() is False:
            return redirect(url_for('auth.login', next=request.path))

        return render_template('page.html', content=markdown(page.html))


@views.route('/settings', methods=['POST', 'GET'])
def settings():
    if authed():
        if request.method == "POST":
            errors = []

            name = request.form.get('name').strip()
            email = request.form.get('email').strip()
            website = request.form.get('website').strip()
            affiliation = request.form.get('affiliation').strip()
            country = request.form.get('country').strip()

            user = Users.query.filter_by(id=session['id']).first()

            if not get_config('prevent_name_change'):
                names = Users.query.filter_by(name=name).first()
                name_len = len(request.form['name']) == 0

            emails = Users.query.filter_by(email=email).first()
            valid_email = validators.validate_email(email)

            if validators.validate_email(name) is True:
                errors.append('Team name cannot be an email address')

            if ('password' in request.form.keys() and not len(request.form['password']) == 0) and \
                    (not bcrypt_sha256.verify(request.form.get('confirm').strip(), user.password)):
                errors.append("Your old password doesn't match what we have.")
            if not valid_email:
                errors.append("That email doesn't look right")
            if not get_config('prevent_name_change') and names and name != session['username']:
                errors.append('That team name is already taken')
            if emails and emails.id != session['id']:
                errors.append('That email has already been used')
            if not get_config('prevent_name_change') and name_len:
                errors.append('Pick a longer team name')
            if website.strip() and not validators.validate_url(website):
                errors.append("That doesn't look like a valid URL")

            if len(errors) > 0:
                return render_template('profile.html', name=name, email=email, website=website,
                                       affiliation=affiliation, country=country, errors=errors)
            else:
                team = Users.query.filter_by(id=session['id']).first()
                if team.name != name:
                    if not get_config('prevent_name_change'):
                        team.name = name
                        session['username'] = team.name
                if team.email != email.lower():
                    team.email = email.lower()
                    if get_config('verify_emails'):
                        team.verified = False

                if 'password' in request.form.keys() and not len(request.form['password']) == 0:
                    team.password = bcrypt_sha256.encrypt(request.form.get('password'))
                team.website = website
                team.affiliation = affiliation
                team.country = country
                db.session.commit()
                db.session.close()
                return redirect(url_for('views.profile'))
        else:
            user = Users.query.filter_by(id=session['id']).first()
            name = user.name
            email = user.email
            website = user.website
            affiliation = user.affiliation
            country = user.country
            prevent_name_change = get_config('prevent_name_change')
            confirm_email = get_config('verify_emails') and not user.verified
            return render_template('profile.html', name=name, email=email, website=website, affiliation=affiliation,
                                   country=country, prevent_name_change=prevent_name_change, confirm_email=confirm_email)
    else:
        return redirect(url_for('auth.login'))


@views.route('/files', defaults={'path': ''})
@views.route('/files/<path:path>')
def file_handler(path):
    f = Files.query.filter_by(location=path).first_or_404()
    if f.challenge_id:
        if not current_user.is_admin():
            if not ctftime():
                if config.view_after_ctf() and ctf_started():
                    pass
                else:
                    abort(403)
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_file(safe_join(upload_folder, f.location))


@views.route('/themes/<theme>/static/<path:path>')
def themes_handler(theme, path):
    filename = safe_join(app.root_path, 'themes', theme, 'static', path)
    if os.path.isfile(filename):
        return send_file(filename)
    else:
        abort(404)
