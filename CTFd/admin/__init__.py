import hashlib
import json
import os
import datetime

from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint, \
    abort, render_template_string, send_file
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_
from sqlalchemy.exc import IntegrityError

from CTFd.utils import admins_only, is_admin, cache, export_ctf, import_ctf
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, \
    DatabaseError
from CTFd.plugins.keys import get_key_class, KEY_CLASSES

from CTFd.admin.statistics import admin_statistics
from CTFd.admin.challenges import admin_challenges
from CTFd.admin.scoreboard import admin_scoreboard
from CTFd.admin.pages import admin_pages
from CTFd.admin.keys import admin_keys
from CTFd.admin.teams import admin_teams

from CTFd import utils

admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
def admin_view():
    if is_admin():
        return redirect(url_for('admin_statistics.admin_stats'))

    return redirect(url_for('auth.login'))


@admin.route('/admin/plugins/<plugin>', methods=['GET', 'POST'])
@admins_only
def admin_plugin_config(plugin):
    if request.method == 'GET':
        plugins_path = os.path.join(app.root_path, 'plugins')

        config_html_plugins = [name for name in os.listdir(plugins_path)
                               if os.path.isfile(os.path.join(plugins_path, name, 'config.html'))]

        if plugin in config_html_plugins:
            config = open(os.path.join(app.root_path, 'plugins', plugin, 'config.html')).read()
            return render_template_string(config)
        abort(404)
    elif request.method == 'POST':
        for k, v in request.form.items():
            if k == "nonce":
                continue
            utils.set_config(k, v)
        with app.app_context():
            cache.clear()
        return '1'


@admin.route('/admin/import', methods=['GET', 'POST'])
@admins_only
def admin_import_ctf():
    backup = request.files['backup']
    segments = request.form.get('segments')
    errors = []
    try:
        if segments:
            import_ctf(backup, segments=segments.split(','))
        else:
            import_ctf(backup)
    except Exception as e:
        print(e)
        errors.append(type(e).__name__)

    if errors:
        return errors[0], 500
    else:
        return redirect(url_for('admin.admin_config'))


@admin.route('/admin/export', methods=['GET', 'POST'])
@admins_only
def admin_export_ctf():
    segments = request.args.get('segments')
    if segments:
        backup = export_ctf(segments.split(','))
    else:
        backup = export_ctf()
    ctf_name = utils.ctf_name()
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    full_name = "{}.{}.zip".format(ctf_name, day)
    return send_file(backup, as_attachment=True, attachment_filename=full_name)


@admin.route('/admin/config', methods=['GET', 'POST'])
@admins_only
def admin_config():
    if request.method == "POST":
        start = None
        end = None
        freeze = None
        if request.form.get('start'):
            start = int(request.form['start'])
        if request.form.get('end'):
            end = int(request.form['end'])
        if request.form.get('freeze'):
            freeze = int(request.form['freeze'])

        try:
            # Set checkbox config values
            view_challenges_unregistered = 'view_challenges_unregistered' in request.form
            view_scoreboard_if_authed = 'view_scoreboard_if_authed' in request.form
            hide_scores = 'hide_scores' in request.form
            prevent_registration = 'prevent_registration' in request.form
            prevent_name_change = 'prevent_name_change' in request.form
            view_after_ctf = 'view_after_ctf' in request.form
            verify_emails = 'verify_emails' in request.form
            mail_tls = 'mail_tls' in request.form
            mail_ssl = 'mail_ssl' in request.form
            mail_useauth = 'mail_useauth' in request.form
            workshop_mode = 'workshop_mode' in request.form
            paused = 'paused' in request.form
        finally:
            utils.set_config('view_challenges_unregistered', view_challenges_unregistered)
            utils.set_config('view_scoreboard_if_authed', view_scoreboard_if_authed)
            utils.set_config('hide_scores', hide_scores)
            utils.set_config('prevent_registration', prevent_registration)
            utils.set_config('prevent_name_change', prevent_name_change)
            utils.set_config('view_after_ctf', view_after_ctf)
            utils.set_config('verify_emails', verify_emails)
            utils.set_config('mail_tls', mail_tls)
            utils.set_config('mail_ssl', mail_ssl)
            utils.set_config('mail_useauth', mail_useauth)
            utils.set_config('workshop_mode', workshop_mode)
            utils.set_config('paused', paused)

        utils.set_config("mail_server", request.form.get('mail_server', None))
        utils.set_config("mail_port", request.form.get('mail_port', None))

        if request.form.get('mail_useauth', None) and (request.form.get('mail_u', None) or request.form.get('mail_p', None)):
            if len(request.form.get('mail_u')) > 0:
                utils.set_config("mail_username", request.form.get('mail_u', None))
            if len(request.form.get('mail_p')) > 0:
                utils.set_config("mail_password", request.form.get('mail_p', None))

        elif request.form.get('mail_useauth', None) is None:
            utils.set_config("mail_username", None)
            utils.set_config("mail_password", None)

        if request.files.get('ctf_logo_file', None):
            ctf_logo = request.files['ctf_logo_file']
            file_id, file_loc = utils.upload_file(ctf_logo, None)
            utils.set_config("ctf_logo", file_loc)
        elif request.form.get('ctf_logo') == '':
            utils.set_config("ctf_logo", None)

        utils.set_config("ctf_name", request.form.get('ctf_name', None))
        utils.set_config("ctf_theme", request.form.get('ctf_theme', None))
        utils.set_config('css', request.form.get('css', None))

        utils.set_config("mailfrom_addr", request.form.get('mailfrom_addr', None))
        utils.set_config("mg_base_url", request.form.get('mg_base_url', None))
        utils.set_config("mg_api_key", request.form.get('mg_api_key', None))

        utils.set_config("freeze", freeze)

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

    # Clear the cache so that we don't get stale values
    cache.clear()

    ctf_name = utils.get_config('ctf_name')
    ctf_logo = utils.get_config('ctf_logo')
    ctf_theme = utils.get_config('ctf_theme')
    hide_scores = utils.get_config('hide_scores')
    css = utils.get_config('css')

    mail_server = utils.get_config('mail_server')
    mail_port = utils.get_config('mail_port')
    mail_username = utils.get_config('mail_username')
    mail_password = utils.get_config('mail_password')

    mailfrom_addr = utils.get_config('mailfrom_addr')
    mg_api_key = utils.get_config('mg_api_key')
    mg_base_url = utils.get_config('mg_base_url')

    view_after_ctf = utils.get_config('view_after_ctf')
    start = utils.get_config('start')
    end = utils.get_config('end')
    freeze = utils.get_config('freeze')

    mail_tls = utils.get_config('mail_tls')
    mail_ssl = utils.get_config('mail_ssl')
    mail_useauth = utils.get_config('mail_useauth')

    view_challenges_unregistered = utils.get_config('view_challenges_unregistered')
    view_scoreboard_if_authed = utils.get_config('view_scoreboard_if_authed')
    prevent_registration = utils.get_config('prevent_registration')
    prevent_name_change = utils.get_config('prevent_name_change')
    verify_emails = utils.get_config('verify_emails')

    workshop_mode = utils.get_config('workshop_mode')
    paused = utils.get_config('paused')

    db.session.commit()
    db.session.close()

    themes = utils.get_themes()
    themes.remove(ctf_theme)

    return render_template(
        'admin/config.html',
        ctf_name=ctf_name,
        ctf_logo=ctf_logo,
        ctf_theme_config=ctf_theme,
        css=css,
        start=start,
        end=end,
        freeze=freeze,
        hide_scores=hide_scores,
        mail_server=mail_server,
        mail_port=mail_port,
        mail_useauth=mail_useauth,
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
        themes=themes,
        workshop_mode=workshop_mode,
        paused=paused
    )
