from flask import render_template, request, redirect, url_for, Blueprint
from CTFd.models import db, Teams
from CTFd.utils.decorators import authed_only, ratelimit
from CTFd.utils.decorators.modes import require_team_mode
from CTFd.utils import config
from CTFd.utils.user import get_current_user
from CTFd.utils.crypto import verify_password
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers import get_errors

teams = Blueprint("teams", __name__)


@teams.route("/teams")
@check_account_visibility
@require_team_mode
def listing():
    page = abs(request.args.get("page", 1, type=int))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    # TODO: Should teams confirm emails?
    # if get_config('verify_emails'):
    #     count = Teams.query.filter_by(verified=True, banned=False).count()
    #     teams = Teams.query.filter_by(verified=True, banned=False).slice(page_start, page_end).all()
    # else:
    count = Teams.query.filter_by(hidden=False, banned=False).count()
    teams = (
        Teams.query.filter_by(hidden=False, banned=False)
        .slice(page_start, page_end)
        .all()
    )

    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template("teams/teams.html", teams=teams, pages=pages, curr_page=page)


@teams.route("/teams/join", methods=["GET", "POST"])
@authed_only
@require_team_mode
@ratelimit(method="POST", limit=10, interval=5)
def join():
    if request.method == "GET":
        return render_template("teams/join_team.html")
    if request.method == "POST":
        teamname = request.form.get("name")
        passphrase = request.form.get("password", "").strip()

        team = Teams.query.filter_by(name=teamname).first()
        user = get_current_user()
        if team and verify_password(passphrase, team.password):
            user.team_id = team.id
            db.session.commit()

            if len(team.members) == 1:
                team.captain_id = user.id
                db.session.commit()

            return redirect(url_for("challenges.listing"))
        else:
            errors = ["That information is incorrect"]
            return render_template("teams/join_team.html", errors=errors)


@teams.route("/teams/new", methods=["GET", "POST"])
@authed_only
@require_team_mode
def new():
    if request.method == "GET":
        return render_template("teams/new_team.html")
    elif request.method == "POST":
        teamname = request.form.get("name")
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
