import csv  # noqa: I001
import datetime
from io import StringIO
import os

from flask import Blueprint, abort
from flask import current_app as app
from flask import (
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    url_for,
)

admin = Blueprint("admin", __name__)

# isort:imports-firstparty
from CTFd.admin import challenges  # noqa: F401,I001
from CTFd.admin import notifications  # noqa: F401,I001
from CTFd.admin import pages  # noqa: F401,I001
from CTFd.admin import scoreboard  # noqa: F401,I001
from CTFd.admin import statistics  # noqa: F401,I001
from CTFd.admin import submissions  # noqa: F401,I001
from CTFd.admin import teams  # noqa: F401,I001
from CTFd.admin import users  # noqa: F401,I001
from CTFd.cache import (
    cache,
    clear_challenges,
    clear_config,
    clear_pages,
    clear_standings,
)
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
)
from CTFd.utils import config as ctf_config
from CTFd.utils import get_config, set_config
from CTFd.utils.csv import dump_csv, load_challenges_csv, load_teams_csv, load_users_csv
from CTFd.utils.decorators import admins_only
from CTFd.utils.exports import background_import_ctf
from CTFd.utils.exports import export_ctf as export_ctf_util
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


@admin.route("/admin/import", methods=["GET", "POST"])
@admins_only
def import_ctf():
    if request.method == "GET":
        start_time = cache.get("import_start_time")
        end_time = cache.get("import_end_time")
        import_status = cache.get("import_status")
        import_error = cache.get("import_error")
        return render_template(
            "admin/import.html",
            start_time=start_time,
            end_time=end_time,
            import_status=import_status,
            import_error=import_error,
        )
    elif request.method == "POST":
        backup = request.files["backup"]
        background_import_ctf(backup)
        return redirect(url_for("admin.import_ctf"))


@admin.route("/admin/export", methods=["GET", "POST"])
@admins_only
def export_ctf():
    backup = export_ctf_util()
    ctf_name = ctf_config.ctf_name()
    day = datetime.datetime.now().strftime("%Y-%m-%d_%T")
    full_name = u"{}.{}.zip".format(ctf_name, day)
    return send_file(
        backup, cache_timeout=-1, as_attachment=True, attachment_filename=full_name
    )


@admin.route("/admin/import/csv", methods=["POST"])
@admins_only
def import_csv():
    csv_type = request.form["csv_type"]
    # Try really hard to load data in properly no matter what nonsense Excel gave you
    raw = request.files["csv_file"].stream.read()
    try:
        csvdata = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            csvdata = raw.decode("cp1252")
        except UnicodeDecodeError:
            csvdata = raw.decode("latin-1")
    csvfile = StringIO(csvdata)

    loaders = {
        "challenges": load_challenges_csv,
        "users": load_users_csv,
        "teams": load_teams_csv,
    }

    loader = loaders[csv_type]
    reader = csv.DictReader(csvfile)
    success = loader(reader)
    if success is True:
        return redirect(url_for("admin.config"))
    else:
        return jsonify(success), 500


@admin.route("/admin/export/csv")
@admins_only
def export_csv():
    table = request.args.get("table")

    output = dump_csv(name=table)

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
    configs = {c.key: get_config(c.key) for c in configs}

    themes = ctf_config.get_themes()

    # Remove current theme but ignore failure
    try:
        themes.remove(get_config("ctf_theme"))
    except ValueError:
        pass

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
        clear_challenges()
        clear_config()

        if logout is True:
            cache.clear()
            logout_user()

        db.session.close()
        return redirect(next_url)

    return render_template("admin/reset.html")
