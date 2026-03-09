import os

from flask import Blueprint, abort, jsonify, render_template, request, url_for
from sqlalchemy.sql.expression import union_all
from werkzeug.utils import secure_filename

from collections import defaultdict

from CTFd.cache import cache
from CTFd.models import Awards, Challenges, Solves, Users, db
from CTFd.plugins import (
    bypass_csrf_protection,
    override_template,
    register_admin_plugin_menu_bar,
    register_plugin_assets_directory,
    register_user_page_menu_bar,
)
from CTFd.utils import get_config
from CTFd.utils.dates import isoformat, unix_time_to_utc
from CTFd.utils.decorators import admins_only
from CTFd.utils.uploads import upload_file

from .models import Units, UserUnits

PLUGIN_DIR = os.path.dirname(__file__)

units_bp = Blueprint(
    "units", __name__, template_folder="templates", static_folder="assets"
)


def get_units():
    return Units.query.order_by(Units.name).all()


def get_unit_scoreboard_data():
    """Build unit scoreboard: aggregate member scores per unit."""
    # Solve scores per user
    scores = (
        db.session.query(
            Solves.user_id.label("user_id"),
            db.func.sum(Challenges.value).label("score"),
            db.func.max(Solves.id).label("id"),
            db.func.max(Solves.date).label("date"),
        )
        .join(Challenges)
        .filter(Challenges.value != 0)
        .group_by(Solves.user_id)
    )

    # Award scores per user
    awards = (
        db.session.query(
            Awards.user_id.label("user_id"),
            db.func.sum(Awards.value).label("score"),
            db.func.max(Awards.id).label("id"),
            db.func.max(Awards.date).label("date"),
        )
        .filter(Awards.value != 0)
        .group_by(Awards.user_id)
    )

    # Respect freeze time
    freeze = get_config("freeze")
    if freeze:
        scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
        awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

    # Union solves + awards
    results = union_all(scores, awards).alias("results")

    # Sum per user
    user_scores = (
        db.session.query(
            results.columns.user_id,
            db.func.sum(results.columns.score).label("score"),
        )
        .group_by(results.columns.user_id)
        .subquery()
    )

    # Aggregate per unit, filtering banned/hidden users
    unit_standings = (
        db.session.query(
            Units.id.label("unit_id"),
            Units.name.label("name"),
            Units.emblem_path.label("emblem_path"),
            db.func.coalesce(db.func.sum(user_scores.columns.score), 0).label("score"),
            db.func.count(UserUnits.user_id).label("member_count"),
        )
        .join(UserUnits, Units.id == UserUnits.unit_id)
        .join(Users, Users.id == UserUnits.user_id)
        .outerjoin(user_scores, Users.id == user_scores.columns.user_id)
        .filter(Users.banned == False, Users.hidden == False)
        .group_by(Units.id, Units.name, Units.emblem_path)
        .order_by(db.text("score DESC"))
        .all()
    )

    standings = []
    for pos, row in enumerate(unit_standings, 1):
        emblem_url = ""
        if row.emblem_path:
            emblem_url = url_for("views.files", path=row.emblem_path)
        standings.append(
            {
                "pos": pos,
                "unit_id": row.unit_id,
                "name": row.name,
                "emblem_url": emblem_url,
                "score": int(row.score),
                "member_count": row.member_count,
            }
        )
    return standings


def get_unit_scoreboard_detail():
    """Return per-unit solve history for charting cumulative scores over time."""
    freeze = get_config("freeze")

    # Get all solves with challenge values
    solves_q = (
        db.session.query(
            Solves.user_id,
            Challenges.value.label("value"),
            Solves.date.label("date"),
        )
        .join(Challenges)
        .filter(Challenges.value != 0)
    )

    # Get all awards
    awards_q = (
        db.session.query(
            Awards.user_id,
            Awards.value.label("value"),
            Awards.date.label("date"),
        )
        .filter(Awards.value != 0)
    )

    if freeze:
        solves_q = solves_q.filter(Solves.date < unix_time_to_utc(freeze))
        awards_q = awards_q.filter(Awards.date < unix_time_to_utc(freeze))

    # Map user_id -> unit info
    user_unit_map = {}
    unit_info = {}
    rows = (
        db.session.query(UserUnits.user_id, Units.id, Units.name, Units.emblem_path)
        .join(Units, Units.id == UserUnits.unit_id)
        .join(Users, Users.id == UserUnits.user_id)
        .filter(Users.banned == False, Users.hidden == False)
        .all()
    )
    for user_id, unit_id, unit_name, emblem_path in rows:
        user_unit_map[user_id] = unit_id
        if unit_id not in unit_info:
            emblem_url = ""
            if emblem_path:
                emblem_url = url_for("views.files", path=emblem_path)
            unit_info[unit_id] = {"name": unit_name, "emblem_url": emblem_url}

    # Collect events per unit: list of {value, date}
    unit_events = defaultdict(list)

    for user_id, value, date in solves_q.all():
        uid = user_unit_map.get(user_id)
        if uid:
            unit_events[uid].append({"value": int(value), "date": isoformat(date)})

    for user_id, value, date in awards_q.all():
        uid = user_unit_map.get(user_id)
        if uid:
            unit_events[uid].append({"value": int(value), "date": isoformat(date)})

    # Sort events by date and build response
    result = {}
    for i, (unit_id, info) in enumerate(
        sorted(
            unit_info.items(),
            key=lambda x: sum(e["value"] for e in unit_events.get(x[0], [])),
            reverse=True,
        )
    ):
        events = sorted(unit_events.get(unit_id, []), key=lambda e: e["date"])
        result[i + 1] = {
            "id": unit_id,
            "name": info["name"],
            "emblem_url": info["emblem_url"],
            "score": sum(e["value"] for e in events),
            "solves": events,
        }

    return result


def get_user_unit(user_id):
    """Return unit info dict for a user, or None if not assigned."""
    user_unit = UserUnits.query.filter_by(user_id=user_id).first()
    if not user_unit:
        return None
    unit = Units.query.filter_by(id=user_unit.unit_id).first()
    if not unit:
        return None
    return {
        "id": unit.id,
        "name": unit.name,
        "emblem_url": url_for("views.files", path=unit.emblem_path)
        if unit.emblem_path
        else "",
    }


def load(app):
    app.db.create_all()

    # Register blueprint so templates/ folder is on Jinja search path
    app.register_blueprint(units_bp)

    # Register static assets
    register_plugin_assets_directory(
        app, base_path="/plugins/units/assets"
    )

    # Override templates
    overrides = {
        "register.html": "register_override.html",
        "users/private.html": "users/private.html",
        "users/public.html": "users/public.html",
    }
    for core_template, plugin_template in overrides.items():
        path = os.path.join(PLUGIN_DIR, "templates", plugin_template)
        with open(path, "r") as f:
            override_template(core_template, f.read())

    # Make helper functions available in Jinja templates
    app.jinja_env.globals["get_units"] = get_units
    app.jinja_env.globals["get_user_unit"] = get_user_unit

    # --- After-request hook: save unit_id on registration ---
    @app.after_request
    def save_unit_on_register(response):
        if (
            request.endpoint == "auth.register"
            and request.method == "POST"
            and response.status_code in (200, 302)
        ):
            # Check if the response is a redirect (successful registration)
            if response.status_code != 302:
                return response

            unit_id = request.form.get("unit_id")
            if not unit_id:
                return response

            # Handle creating a new unit
            if unit_id == "__new__":
                new_name = request.form.get("new_unit_name", "").strip()
                if not new_name:
                    return response

                # Use existing unit if the name is already taken
                existing_unit = Units.query.filter_by(name=new_name).first()
                if existing_unit:
                    unit_id = existing_unit.id
                else:
                    unit = Units(name=new_name, description="")
                    db.session.add(unit)
                    db.session.flush()
                    unit_id = unit.id
            else:
                try:
                    unit_id = int(unit_id)
                except (ValueError, TypeError):
                    return response

                if not Units.query.filter_by(id=unit_id).first():
                    return response

            # Find the most recently created user with the submitted name
            name = request.form.get("name", "").strip()
            user = Users.query.filter_by(name=name).first()
            if not user:
                return response

            # Don't duplicate
            existing = UserUnits.query.filter_by(user_id=user.id).first()
            if not existing:
                db.session.add(UserUnits(user_id=user.id, unit_id=unit_id))
                db.session.commit()

        return response

    # --- Admin routes ---
    @app.route("/admin/units", methods=["GET"])
    @admins_only
    def admin_units_page():
        units = Units.query.order_by(Units.name).all()
        return render_template("admin_units.html", units=units)

    # --- API: list units ---
    @app.route("/api/v1/units/", methods=["GET"])
    def api_list_units():
        units = Units.query.order_by(Units.name).all()
        return jsonify(
            {
                "success": True,
                "data": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "description": u.description,
                        "emblem_url": url_for("views.files", path=u.emblem_path)
                        if u.emblem_path
                        else "",
                    }
                    for u in units
                ],
            }
        )

    # --- API: create unit ---
    @app.route("/api/v1/units/", methods=["POST"])
    @admins_only
    @bypass_csrf_protection
    def api_create_unit():
        name = request.form.get("name", "").strip()
        if not name:
            return jsonify({"success": False, "errors": {"name": "Name is required"}}), 400

        if Units.query.filter_by(name=name).first():
            return jsonify({"success": False, "errors": {"name": "A unit with that name already exists"}}), 400

        description = request.form.get("description", "").strip()
        emblem_path = ""

        emblem = request.files.get("emblem")
        if emblem and emblem.filename:
            filename = secure_filename(emblem.filename)
            location = f"unit_emblems/{filename}"
            file_row = upload_file(file=emblem, location=location)
            emblem_path = file_row.location

        unit = Units(name=name, description=description, emblem_path=emblem_path)
        db.session.add(unit)
        db.session.commit()

        return jsonify({"success": True, "data": {"id": unit.id, "name": unit.name}}), 201

    # --- API: update unit ---
    @app.route("/api/v1/units/<int:unit_id>", methods=["PATCH"])
    @admins_only
    @bypass_csrf_protection
    def api_update_unit(unit_id):
        unit = Units.query.filter_by(id=unit_id).first_or_404()

        name = request.form.get("name")
        if name is not None:
            name = name.strip()
            if not name:
                return jsonify({"success": False, "errors": {"name": "Name cannot be empty"}}), 400
            dupe = Units.query.filter(Units.name == name, Units.id != unit_id).first()
            if dupe:
                return jsonify({"success": False, "errors": {"name": "A unit with that name already exists"}}), 400
            unit.name = name

        description = request.form.get("description")
        if description is not None:
            unit.description = description.strip()

        emblem = request.files.get("emblem")
        if emblem and emblem.filename:
            filename = secure_filename(emblem.filename)
            location = f"unit_emblems/{filename}"
            file_row = upload_file(file=emblem, location=location)
            unit.emblem_path = file_row.location

        db.session.commit()
        return jsonify({"success": True, "data": {"id": unit.id, "name": unit.name}})

    # --- API: delete unit ---
    @app.route("/api/v1/units/<int:unit_id>", methods=["DELETE"])
    @admins_only
    def api_delete_unit(unit_id):
        unit = Units.query.filter_by(id=unit_id).first_or_404()

        db.session.delete(unit)
        db.session.commit()
        return jsonify({"success": True})

    # --- API: unit scoreboard ---
    @app.route("/api/v1/units/scoreboard", methods=["GET"])
    @cache.cached(timeout=10, key_prefix="units_scoreboard")
    def api_unit_scoreboard():
        return jsonify({"success": True, "data": get_unit_scoreboard_data()})

    # --- API: unit scoreboard detail (for chart) ---
    @app.route("/api/v1/units/scoreboard/detail", methods=["GET"])
    @cache.cached(timeout=10, key_prefix="units_scoreboard_detail")
    def api_unit_scoreboard_detail():
        return jsonify({"success": True, "data": get_unit_scoreboard_detail()})

    # --- Public scoreboard page ---
    @app.route("/units/scoreboard", methods=["GET"])
    def unit_scoreboard_page():
        return render_template("unit_scoreboard.html")

    # Register menu items
    register_admin_plugin_menu_bar("Units", "units")
    register_user_page_menu_bar("Unit Scoreboard", "/units/scoreboard")

    app.logger.info("units: plugin loaded")
