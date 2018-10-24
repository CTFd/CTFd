from flask import current_app as app, render_template, request, redirect, abort, jsonify, url_for, session, Blueprint, Response, send_file
from flask.helpers import safe_join
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Admins, Files, Pages, Announcements
from CTFd.utils import markdown
from CTFd.cache import cache
from CTFd.utils import get_config, set_config
from CTFd.utils.user import authed, get_current_user
from CTFd.utils import config
from CTFd.utils.config.pages import get_page
from CTFd.utils.security.auth import login_user
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import user as current_user
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, unix_time_to_utc
from CTFd.utils import validators
from CTFd.utils.decorators import authed_only

import os

views = Blueprint('views', __name__)


@views.route('/setup', methods=['GET', 'POST'])
def setup():
    if not config.is_setup():
        if not session.get('nonce'):
            session['nonce'] = generate_nonce()
        if request.method == 'POST':
            ctf_name = request.form['ctf_name']
            set_config('ctf_name', ctf_name)

            # CSS
            set_config('start', '')

            # Admin user
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            admin = Admins(
                name=name,
                email=email,
                password=password,
                type='admin',
                hidden=True
            )

            user_mode = request.form['user_mode']

            set_config('user_mode', user_mode)

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
                content=index,
                draft=False
            )

            # max attempts per challenge
            set_config('max_tries', 0)

            # Start time
            set_config('start', None)
            set_config('end', None)
            set_config('freeze', None)

            # Challenges cannot be viewed by unregistered users
            set_config('view_challenges_unregistered', None)

            # Allow/Disallow registration
            set_config('prevent_registration', None)

            # Verify emails
            set_config('verify_emails', None)

            set_config('mail_server', None)
            set_config('mail_port', None)
            set_config('mail_tls', None)
            set_config('mail_ssl', None)
            set_config('mail_username', None)
            set_config('mail_password', None)
            set_config('mail_useauth', None)

            setup = set_config('setup', True)

            db.session.add(page)
            db.session.add(admin)
            db.session.commit()

            login_user(admin)

            db.session.close()
            app.setup = False
            with app.app_context():
                cache.clear()

            return redirect(url_for('views.static_html'))
        return render_template('setup.html', nonce=session.get('nonce'))
    return redirect(url_for('views.static_html'))


@views.route('/announcements', methods=['GET'])
def announcements():
    announce_list = Announcements.query.order_by(Announcements.id.desc()).all()
    return render_template('announcements.html', announcements=announce_list)


@views.route('/settings', methods=['GET'])
@authed_only
def settings():
    user = get_current_user()
    name = user.name
    email = user.email
    website = user.website
    affiliation = user.affiliation
    country = user.country
    prevent_name_change = get_config('prevent_name_change')
    confirm_email = get_config('verify_emails') and not user.verified
    return render_template(
        'settings.html',
        name=name,
        email=email,
        website=website,
        affiliation=affiliation,
        country=country,
        prevent_name_change=prevent_name_change,
        confirm_email=confirm_email
    )


@views.route('/static/user.css')
@cache.cached(timeout=300)
def custom_css():
    """
    Custom CSS Handler route
    :return:
    """
    return Response(get_config('css'), mimetype='text/css')


# Static HTML files
@views.route("/", defaults={'template': 'index'})
@views.route("/<path:template>")
def static_html(template):
    """
    Route in charge of routing users to Pages.
    :param template:
    :return:
    """
    page = get_page(template)
    if page is None:
        abort(404)
    else:
        if page.auth_required and authed() is False:
            return redirect(url_for('auth.login', next=request.path))

        return render_template('page.html', content=markdown(page.content))


@views.route('/files', defaults={'path': ''})
@views.route('/files/<path:path>')
def file_handler(path):
    """
    Route in charge of dealing with making sure that CTF challenges are only accessible during the competition.
    :param path:
    :return:
    """
    f = Files.query.filter_by(location=path).first_or_404()
    if f.type == 'challenge':
        if current_user.is_admin() is False:
            if not ctftime():
                if config.view_after_ctf() and ctf_started():
                    pass
                else:
                    abort(403)
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_file(safe_join(upload_folder, f.location))


@views.route('/themes/<theme>/static/<path:path>')
def themes_handler(theme, path):
    """
    General static file handler
    :param theme:
    :param path:
    :return:
    """
    filename = safe_join(app.root_path, 'themes', theme, 'static', path)
    if os.path.isfile(filename):
        return send_file(filename)
    else:
        abort(404)
