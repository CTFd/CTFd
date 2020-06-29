from flask import Blueprint, redirect, render_template, request, url_for

from CTFd.cache import clear_team_session, clear_user_session
from CTFd.models import Teams, db
from CTFd.utils import config, get_config
from CTFd.utils.crypto import verify_password
from CTFd.utils.decorators import authed_only, ratelimit
from CTFd.utils.decorators.modes import require_team_mode
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers import get_errors, get_infos
from CTFd.utils.user import get_current_user

teams = Blueprint("teams", __name__)


@teams.route("/teams")
@check_account_visibility
@require_team_mode
def listing():
    q = request.args.get("q")
    field = request.args.get("field", "name")
    filters = []

    if field not in ("name", "affiliation", "website"):
        field = "name"

    if q:
        filters.append(getattr(Teams, field).like("%{}%".format(q)))

    teams = (
        Teams.query.filter_by(hidden=False, banned=False)
        .filter(*filters)
        .order_by(Teams.id.asc())
        .paginate(per_page=50)
    )

    args = dict(request.args)
    args.pop("page", 1)

    return render_template(
        "teams/teams.html",
        teams=teams,
        prev_page=url_for(request.endpoint, page=teams.prev_num, **args),
        next_page=url_for(request.endpoint, page=teams.next_num, **args),
        q=q,
        field=field,
    )


@teams.route("/teams/join", methods=["GET", "POST"])
@authed_only
@require_team_mode
@ratelimit(method="POST", limit=10, interval=5)
def join():
    infos = get_infos()
    errors = get_errors()
    if request.method == "GET":
        team_size_limit = get_config("team_size", default=0)
        if team_size_limit:
            plural = "" if team_size_limit == 1 else "s"
            infos.append(
                "Teams are limited to {limit} member{plural}".format(
                    limit=team_size_limit, plural=plural
                )
            )
        return render_template("teams/join_team.html", infos=infos, errors=errors)

    if request.method == "POST":
        teamname = request.form.get("name")
        passphrase = request.form.get("password", "").strip()

        team = Teams.query.filter_by(name=teamname).first()

        if team and verify_password(passphrase, team.password):
            team_size_limit = get_config("team_size", default=0)
            if team_size_limit and len(team.members) >= team_size_limit:
                errors.append(
                    "{name} has already reached the team size limit of {limit}".format(
                        name=team.name, limit=team_size_limit
                    )
                )
                return render_template(
                    "teams/join_team.html", infos=infos, errors=errors
                )

            user = get_current_user()
            user.team_id = team.id
            db.session.commit()

            if len(team.members) == 1:
                team.captain_id = user.id
                db.session.commit()

            clear_user_session(user_id=user.id)
            clear_team_session(team_id=team.id)

            return redirect(url_for("challenges.listing"))
        else:
            errors.append("That information is incorrect")
            return render_template("teams/join_team.html", infos=infos, errors=errors)


@teams.route("/teams/new", methods=["GET", "POST"])
@authed_only
@require_team_mode
def new():
    infos = get_infos()
    errors = get_errors()
    if request.method == "GET":
        team_size_limit = get_config("team_size", default=0)
        if team_size_limit:
            plural = "" if team_size_limit == 1 else "s"
            infos.append(
                "Teams are limited to {limit} member{plural}".format(
                    limit=team_size_limit, plural=plural
                )
            )

        return render_template("teams/new_team.html", infos=infos, errors=errors)
    elif request.method == "POST":
        teamname = request.form.get("name", "").strip()
        passphrase = request.form.get("password", "").strip()
        errors = get_errors()

        user = get_current_user()

        existing_team = Teams.query.filter_by(name=teamname).first()
        if existing_team:
            errors.append("That team name is already taken")
        if not teamname:
            errors.append("That team name is invalid")

        if errors:
            return render_template("teams/new_team.html", errors=errors)

        team = Teams(name=teamname, password=passphrase, captain_id=user.id)

        db.session.add(team)
        db.session.commit()

        user.team_id = team.id
        db.session.commit()

        clear_user_session(user_id=user.id)
        clear_team_session(team_id=team.id)

        return redirect(url_for("challenges.listing"))


@teams.route("/team")
@authed_only
@require_team_mode
def private():
    user = get_current_user()
    if not user.team_id:
        return render_template("teams/team_enrollment.html")

    team_id = user.team_id

    team = Teams.query.filter_by(id=team_id).first_or_404()
    solves = team.get_solves()
    awards = team.get_awards()

    place = team.place
    score = team.score

    return render_template(
        "teams/private.html",
        solves=solves,
        awards=awards,
        user=user,
        team=team,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen(),
    )


@teams.route("/teams/<int:team_id>")
@check_account_visibility
@check_score_visibility
@require_team_mode
def public(team_id):
    errors = get_errors()
    team = Teams.query.filter_by(id=team_id, banned=False, hidden=False).first_or_404()
    solves = team.get_solves()
    awards = team.get_awards()

    place = team.place
    score = team.score

    if errors:
        return render_template("teams/public.html", team=team, errors=errors)

    return render_template(
        "teams/public.html",
        solves=solves,
        awards=awards,
        team=team,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen(),
    )
