import hashlib
import json
import os

from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint, \
    abort, render_template_string
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd.utils import admins_only, is_admin, unix_time, get_config, \
    set_config, sendmail, rmdir, create_image, delete_image, run_image, container_status, container_ports, \
    container_stop, container_start, get_themes, cache, upload_file, get_configurable_plugins
from CTFd.models import db, Teams, Solves, Awards, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError
from CTFd.scoreboard import get_standings
from CTFd.plugins.keys import get_key_class, KEY_CLASSES

from CTFd.admin.statistics import admin_statistics
from CTFd.admin.challenges import admin_challenges
from CTFd.admin.scoreboard import admin_scoreboard
from CTFd.admin.pages import admin_pages
from CTFd.admin.containers import admin_containers
from CTFd.admin.keys import admin_keys
from CTFd.admin.teams import admin_teams


admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
def admin_view():
    if is_admin():
        return redirect(url_for('admin_statistics.admin_graphs'))

    return redirect(url_for('auth.login'))


@admin.route('/admin/plugins/<plugin>', methods=['GET', 'POST'])
@admins_only
def admin_plugin_config(plugin):
    if request.method == 'GET':
        if plugin in get_configurable_plugins():
            config = open(os.path.join(app.root_path, 'plugins', plugin, 'config.html')).read()
            return render_template('admin/page.html', content=config)
        abort(404)
    elif request.method == 'POST':
        for k, v in request.form.items():
            set_config(k, v)
        return '1'


@admin.route('/admin/config', methods=['GET', 'POST'])
@admins_only
def admin_config():
    if request.method == "POST":
        start = None
        end = None
        if request.form.get('start'):
            start = int(request.form['start'])
        if request.form.get('end'):
            end = int(request.form['end'])

        try:
            view_challenges_unregistered = bool(request.form.get('view_challenges_unregistered', None))
            view_scoreboard_if_authed = bool(request.form.get('view_scoreboard_if_authed', None))
            hide_scores = bool(request.form.get('hide_scores', None))
            prevent_registration = bool(request.form.get('prevent_registration', None))
            prevent_name_change = bool(request.form.get('prevent_name_change', None))
            view_after_ctf = bool(request.form.get('view_after_ctf', None))
            verify_emails = bool(request.form.get('verify_emails', None))
            mail_tls = bool(request.form.get('mail_tls', None))
            mail_ssl = bool(request.form.get('mail_ssl', None))
        except (ValueError, TypeError):
            view_challenges_unregistered = None
            view_scoreboard_if_authed = None
            hide_scores = None
            prevent_registration = None
            prevent_name_change = None
            view_after_ctf = None
            verify_emails = None
            mail_tls = None
            mail_ssl = None
        finally:
            view_challenges_unregistered = set_config('view_challenges_unregistered', view_challenges_unregistered)
            view_scoreboard_if_authed = set_config('view_scoreboard_if_authed', view_scoreboard_if_authed)
            hide_scores = set_config('hide_scores', hide_scores)
            prevent_registration = set_config('prevent_registration', prevent_registration)
            prevent_name_change = set_config('prevent_name_change', prevent_name_change)
            view_after_ctf = set_config('view_after_ctf', view_after_ctf)
            verify_emails = set_config('verify_emails', verify_emails)
            mail_tls = set_config('mail_tls', mail_tls)
            mail_ssl = set_config('mail_ssl', mail_ssl)

        mail_server = set_config("mail_server", request.form.get('mail_server', None))
        mail_port = set_config("mail_port", request.form.get('mail_port', None))

        mail_username = set_config("mail_username", request.form.get('mail_username', None))
        mail_password = set_config("mail_password", request.form.get('mail_password', None))

        ctf_name = set_config("ctf_name", request.form.get('ctf_name', None))
        ctf_theme = set_config("ctf_theme", request.form.get('ctf_theme', None))

        mailfrom_addr = set_config("mailfrom_addr", request.form.get('mailfrom_addr', None))
        mg_base_url = set_config("mg_base_url", request.form.get('mg_base_url', None))
        mg_api_key = set_config("mg_api_key", request.form.get('mg_api_key', None))

        db_start = Config.query.filter_by(key='start').first()
        db_start.value = start

        db_end = Config.query.filter_by(key='end').first()
        db_end.value = end

        db.session.add(db_start)
        db.session.add(db_end)

        db.session.commit()
        db.session.close()
        with app.app_context():
            cache.clear()
        return redirect(url_for('admin.admin_config'))

    with app.app_context():
        cache.clear()
    ctf_name = get_config('ctf_name')
    ctf_theme = get_config('ctf_theme')
    hide_scores = get_config('hide_scores')

    mail_server = get_config('mail_server')
    mail_port = get_config('mail_port')
    mail_username = get_config('mail_username')
    mail_password = get_config('mail_password')

    mailfrom_addr = get_config('mailfrom_addr')
    mg_api_key = get_config('mg_api_key')
    mg_base_url = get_config('mg_base_url')

    view_after_ctf = get_config('view_after_ctf')
    start = get_config('start')
    end = get_config('end')

    mail_tls = get_config('mail_tls')
    mail_ssl = get_config('mail_ssl')

    view_challenges_unregistered = get_config('view_challenges_unregistered')
    view_scoreboard_if_authed = get_config('view_scoreboard_if_authed')
    prevent_registration = get_config('prevent_registration')
    prevent_name_change = get_config('prevent_name_change')
    verify_emails = get_config('verify_emails')

    db.session.commit()
    db.session.close()

    themes = get_themes()
    themes.remove(ctf_theme)

    return render_template('admin/config.html',
                           ctf_name=ctf_name,
                           ctf_theme_config=ctf_theme,
                           start=start,
                           end=end,
                           hide_scores=hide_scores,
                           mail_server=mail_server,
                           mail_port=mail_port,
                           mail_username=mail_username,
                           mail_password=mail_password,
                           mail_tls=mail_tls,
                           mail_ssl=mail_ssl,
                           view_challenges_unregistered=view_challenges_unregistered,
                           view_scoreboard_if_authed=view_scoreboard_if_authed,
                           prevent_registration=prevent_registration,
                           mailfrom_addr=mailfrom_addr,
                           mg_base_url=mg_base_url,
                           mg_api_key=mg_api_key,
                           prevent_name_change=prevent_name_change,
                           verify_emails=verify_emails,
                           view_after_ctf=view_after_ctf,
                           themes=themes)
