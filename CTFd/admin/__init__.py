from flask import current_app as app, render_template, request, redirect, url_for, Blueprint, \
    abort, render_template_string, send_file


from CTFd.utils.decorators import admins_only
from CTFd.utils.user import is_admin
from CTFd.utils import config, cache, validators, uploads, user as current_user, get_config, set_config
from CTFd.utils.exports import export_ctf, import_ctf
from CTFd.models import db, Config

import datetime
import os


admin = Blueprint('admin', __name__)


from CTFd.admin import challenges
from CTFd.admin import pages
from CTFd.admin import scoreboard
from CTFd.admin import statistics
from CTFd.admin import teams


@admin.route('/admin', methods=['GET'])
def admin_view():
    if is_admin():
        return redirect(url_for('admin.admin_stats'))

    return redirect(url_for('auth.login'))


@admin.route('/admin/plugins/<plugin>', methods=['GET', 'POST'])
@admins_only
def admin_plugin_config(plugin):
    if request.method == 'GET':
        plugins_path = os.path.join(app.root_path, 'plugins')

        config_html_plugins = [name for name in os.listdir(plugins_path)
                               if os.path.isfile(os.path.join(plugins_path, name, 'config.html'))]

        if plugin in config_html_plugins:
            config_html = open(os.path.join(app.root_path, 'plugins', plugin, 'config.html')).read()
            return render_template_string(config_html)
        abort(404)
    elif request.method == 'POST':
        for k, v in request.form.items():
            if k == "nonce":
                continue
            set_config(k, v)
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
    ctf_name = config.ctf_name()
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
            set_config('view_challenges_unregistered', view_challenges_unregistered)
            set_config('view_scoreboard_if_authed', view_scoreboard_if_authed)
            set_config('hide_scores', hide_scores)
            set_config('prevent_registration', prevent_registration)
            set_config('prevent_name_change', prevent_name_change)
            set_config('view_after_ctf', view_after_ctf)
            set_config('verify_emails', verify_emails)
            set_config('mail_tls', mail_tls)
            set_config('mail_ssl', mail_ssl)
            set_config('mail_useauth', mail_useauth)
            set_config('workshop_mode', workshop_mode)
            set_config('paused', paused)

        set_config("mail_server", request.form.get('mail_server', None))
        set_config("mail_port", request.form.get('mail_port', None))

        if request.form.get('mail_useauth', None) and (request.form.get('mail_u', None) or request.form.get('mail_p', None)):
            if len(request.form.get('mail_u')) > 0:
                set_config("mail_username", request.form.get('mail_u', None))
            if len(request.form.get('mail_p')) > 0:
                set_config("mail_password", request.form.get('mail_p', None))

        elif request.form.get('mail_useauth', None) is None:
            set_config("mail_username", None)
            set_config("mail_password", None)

        if request.files.get('ctf_logo_file', None):
            ctf_logo = request.files['ctf_logo_file']
            file_id, file_loc = uploads.upload_file(ctf_logo, None)
            set_config("ctf_logo", file_loc)
        elif request.form.get('ctf_logo') == '':
            set_config("ctf_logo", None)

        set_config("ctf_name", request.form.get('ctf_name', None))
        set_config("ctf_theme", request.form.get('ctf_theme', None))
        set_config('css', request.form.get('css', None))

        set_config("mailfrom_addr", request.form.get('mailfrom_addr', None))
        set_config("mg_base_url", request.form.get('mg_base_url', None))
        set_config("mg_api_key", request.form.get('mg_api_key', None))

        set_config("freeze", freeze)

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

    ctf_name = get_config('ctf_name')
    ctf_logo = get_config('ctf_logo')
    ctf_theme = get_config('ctf_theme')
    hide_scores = get_config('hide_scores')
    css = get_config('css')

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
    freeze = get_config('freeze')

    mail_tls = get_config('mail_tls')
    mail_ssl = get_config('mail_ssl')
    mail_useauth = get_config('mail_useauth')

    view_challenges_unregistered = get_config('view_challenges_unregistered')
    view_scoreboard_if_authed = get_config('view_scoreboard_if_authed')
    prevent_registration = get_config('prevent_registration')
    prevent_name_change = get_config('prevent_name_change')
    verify_emails = get_config('verify_emails')

    workshop_mode = get_config('workshop_mode')
    paused = get_config('paused')

    db.session.commit()
    db.session.close()

    themes = config.get_themes()
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
