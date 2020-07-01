import csv
import datetime
import os
from io import BytesIO, StringIO

from flask import Blueprint, abort
from flask import current_app as app
from flask import (
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    url_for,
)

admin = Blueprint("admin", __name__)

# isort:imports-firstparty
from CTFd.admin import challenges  # noqa: F401
from CTFd.admin import notifications  # noqa: F401
from CTFd.admin import pages  # noqa: F401
from CTFd.admin import scoreboard  # noqa: F401
from CTFd.admin import statistics  # noqa: F401
from CTFd.admin import submissions  # noqa: F401
from CTFd.admin import teams  # noqa: F401
from CTFd.admin import users  # noqa: F401
from CTFd.cache import cache, clear_config, clear_pages, clear_standings
from CTFd.models import (
    Awards,
    Challenges,
    Configs,
    Notifications,
    Pages,
    Solves,
    Submissions,
    Teams,
    Tracking,
    Unlocks,
    Users,
    db,
    get_class_by_tablename,
)
from CTFd.utils import config as ctf_config
from CTFd.utils import get_config, set_config
from CTFd.utils.decorators import admins_only
from CTFd.utils.exports import export_ctf as export_ctf_util
from CTFd.utils.exports import import_ctf as import_ctf_util
from CTFd.utils.helpers import get_errors
from CTFd.utils.security.auth import logout_user
from CTFd.utils.uploads import delete_file
from CTFd.utils.user import is_admin


@admin.route("/admin", methods=["GET"])
def view():
    if is_admin():
        return redirect(url_for("admin.statistics"))
    return redirect(url_for("auth.login"))


@admin.route("/admin/plugins/<plugin>", methods=["GET", "POST"])
@admins_only
def plugin(plugin):
    if request.method == "GET":
        plugins_path = os.path.join(app.root_path, "plugins")

        config_html_plugins = [
            name
            for name in os.listdir(plugins_path)
            if os.path.isfile(os.path.join(plugins_path, name, "config.html"))
        ]

        if plugin in config_html_plugins:
            config_html = open(
                os.path.join(app.root_path, "plugins", plugin, "config.html")
            ).read()
            return render_template_string(config_html)
        abort(404)
    elif request.method == "POST":
        for k, v in request.form.items():
            if k == "nonce":
                continue
            set_config(k, v)
        with app.app_context():
            clear_config()
        return "1"


@admin.route("/admin/import", methods=["POST"])
@admins_only
def import_ctf():
    backup = request.files["backup"]
    errors = get_errors()
    try:
        import_ctf_util(backup)
    except Exception as e:
        print(e)
        errors.append(repr(e))

    if errors:
        return errors[0], 500
    else:
        return redirect(url_for("admin.config"))


@admin.route("/admin/export", methods=["GET", "POST"])
@admins_only
def export_ctf():
    backup = export_ctf_util()
    ctf_name = ctf_config.ctf_name()
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    full_name = u"{}.{}.zip".format(ctf_name, day)
    return send_file(
        backup, cache_timeout=-1, as_attachment=True, attachment_filename=full_name
    )


@admin.route("/admin/export/csv")
@admins_only
def export_csv():
    table = request.args.get("table")

    # TODO: It might make sense to limit dumpable tables. Config could potentially leak sensitive information.
    model = get_class_by_tablename(table)
    if model is None:
        abort(404)

    temp = StringIO()
    writer = csv.writer(temp)

    header = [column.name for column in model.__mapper__.columns]
    writer.writerow(header)

    responses = model.query.all()

    for curr in responses:
        writer.writerow(
            [getattr(curr, column.name) for column in model.__mapper__.columns]
        )

    temp.seek(0)

    # In Python 3 send_file requires bytes
    output = BytesIO()
    output.write(temp.getvalue().encode("utf-8"))
    output.seek(0)
    temp.close()

    return send_file(
        output,
        as_attachment=True,
        cache_timeout=-1,
        attachment_filename="{name}-{table}.csv".format(
            name=ctf_config.ctf_name(), table=table
        ),
    )


@admin.route("/admin/config", methods=["GET", "POST"])
@admins_only
def config():
    # Clear the config cache so that we don't get stale values
    clear_config()

    configs = Configs.query.all()
    configs = dict([(c.key, get_config(c.key)) for c in configs])

    themes = ctf_config.get_themes()
    themes.remove(get_config("ctf_theme"))

    return render_template("admin/config.html", themes=themes, **configs)


@admin.route("/admin/reset", methods=["GET", "POST"])
@admins_only
def reset():
    if request.method == "POST":
        require_setup = False
        logout = False
        next_url = url_for("admin.statistics")

        data = request.form

        if data.get("pages"):
            _pages = Pages.query.all()
            for p in _pages:
                for f in p.files:
                    delete_file(file_id=f.id)

            Pages.query.delete()

        if data.get("notifications"):
            Notifications.query.delete()

        if data.get("challenges"):
            _challenges = Challenges.query.all()
            for c in _challenges:
                for f in c.files:
                    delete_file(file_id=f.id)
            Challenges.query.delete()

        if data.get("accounts"):
            Users.query.delete()
            Teams.query.delete()
            require_setup = True
            logout = True

        if data.get("submissions"):
            Solves.query.delete()
            Submissions.query.delete()
            Awards.query.delete()
            Unlocks.query.delete()
            Tracking.query.delete()

        if require_setup:
            set_config("setup", False)
            cache.clear()
            logout_user()
            next_url = url_for("views.setup")

        db.session.commit()

        clear_pages()
        clear_standings()
        clear_config()

        if logout is True:
            cache.clear()
            logout_user()

        db.session.close()
        return redirect(next_url)

    return render_template("admin/reset.html")
