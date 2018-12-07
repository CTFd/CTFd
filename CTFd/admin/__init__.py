from flask import (
    current_app as app,
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
    render_template_string,
    send_file
)

from CTFd.utils.decorators import admins_only
from CTFd.utils.user import is_admin
from CTFd.utils.security.auth import logout_user
from CTFd.utils.config import is_setup
from CTFd.utils import (
    config as ctf_config,
    validators,
    uploads,
    user as current_user,
    get_config,
    get_app_config,
    set_config,
)
from CTFd.cache import cache, clear_config
from CTFd.utils.helpers import get_errors
from CTFd.utils.exports import (
    export_ctf as export_ctf_util,
    import_ctf as import_ctf_util
)
from CTFd.models import (
    db,
    get_class_by_tablename,
    Users,
    Teams,
    Configs,
    Submissions,
    Solves,
    Awards,
    Unlocks,
    Tracking
)
import datetime
import os
import six
import csv


admin = Blueprint('admin', __name__)


from CTFd.admin import challenges
from CTFd.admin import pages
from CTFd.admin import scoreboard
from CTFd.admin import statistics
from CTFd.admin import teams
from CTFd.admin import users
from CTFd.admin import submissions
from CTFd.admin import notifications


@admin.route('/admin', methods=['GET'])
def view():
    if is_admin():
        return redirect(url_for('admin.statistics'))
    return redirect(url_for('auth.login'))


@admin.route('/admin/plugins/<plugin>', methods=['GET', 'POST'])
@admins_only
def plugin(plugin):
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
            clear_config()
        return '1'


@admin.route('/admin/import', methods=['POST'])
@admins_only
def import_ctf():
    backup = request.files['backup']
    segments = request.form.get('segments')
    errors = get_errors()
    try:
        import_ctf_util(backup)
    except Exception as e:
        print(e)
        errors.append(repr(e))

    if errors:
        return errors[0], 500
    else:
        return redirect(url_for('admin.config'))


@admin.route('/admin/export', methods=['GET', 'POST'])
@admins_only
def export_ctf():
    backup = export_ctf_util()
    ctf_name = ctf_config.ctf_name()
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    full_name = u"{}.{}.zip".format(ctf_name, day)
    return send_file(backup, as_attachment=True, attachment_filename=full_name)


@admin.route('/admin/export/csv')
@admins_only
def export_csv():
    table = request.args.get('table')

    # TODO: It might make sense to limit dumpable tables. Config could potentially leak sensitive information.
    model = get_class_by_tablename(table)
    if model is None:
        abort(404)

    output = six.StringIO()
    writer = csv.writer(output)

    header = [column.name for column in model.__mapper__.columns]
    writer.writerow(header)

    responses = model.query.all()

    for curr in responses:
        writer.writerow([getattr(curr, column.name) for column in model.__mapper__.columns])

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        cache_timeout=-1,
        attachment_filename="{name}-{table}.csv".format(name=ctf_config.ctf_name(), table=table)
    )


@admin.route('/admin/config', methods=['GET', 'POST'])
@admins_only
def config():
    # Clear the config cache so that we don't get stale values
    clear_config()

    database_tables = sorted(db.metadata.tables.keys())

    configs = Configs.query.all()
    configs = dict([(c.key, get_config(c.key)) for c in configs])

    themes = ctf_config.get_themes()
    themes.remove(get_config('ctf_theme'))

    return render_template(
        'admin/config.html',
        database_tables=database_tables,
        themes=themes,
        **configs
    )


@admin.route('/admin/reset', methods=['GET', 'POST'])
@admins_only
def reset():
    if request.method == 'POST':
        # Truncate Users, Teams, Submissions, Solves, Notifications, Awards, Unlocks, Tracking
        Tracking.query.delete()
        Solves.query.delete()
        Submissions.query.delete()
        Awards.query.delete()
        Unlocks.query.delete()
        Users.query.delete()
        Teams.query.delete()
        set_config('setup', False)
        db.session.commit()
        cache.clear()
        logout_user()
        db.session.close()
        return redirect(url_for('views.setup'))

    return render_template('admin/reset.html')
