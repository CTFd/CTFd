from flask import render_template, request, url_for
from sqlalchemy.sql import not_

from CTFd.admin import admin
from CTFd.models import Challenges, Tracking, Users, Brackets
from CTFd.utils import get_config
from CTFd.utils.decorators import admins_only
from CTFd.utils.modes import TEAMS_MODE


@admin.route("/admin/users")
@admins_only
def users_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    page = abs(request.args.get("page", 1, type=int))
    filters = []

    # Get 'bracket' filter parameter
    bracket_param = request.args.get("bracket")
    if bracket_param:
        try:
            bracket_param = int(bracket_param)
        except ValueError:
            bracket_param = None

    if q:
        if Users.__mapper__.has_property(field):
            filters.append(getattr(Users, field).like("%{}%".format(q)))

    if q and field == "ip":
        query = Users.query.join(Tracking, Users.id == Tracking.user_id).filter(Tracking.ip.like("%{}%".format(q)))
        if bracket_param:
            query = query.filter(Users.bracket_id == bracket_param)
        users = query.order_by(Users.id.asc()).paginate(page=page, per_page=50, error_out=False)
    else:
        if bracket_param:
            filters.append(Users.bracket_id == bracket_param)
        users = Users.query.filter(*filters).order_by(Users.id.asc()).paginate(page=page, per_page=50, error_out=False)

    args = dict(request.args)
    args.pop("page", 1)

    # Retrieve available brackets for users
    brackets = Brackets.query.filter_by(type="users").all()

    return render_template(
        "admin/users/users.html",
        users=users,
        prev_page=url_for(request.endpoint, page=users.prev_num, **args),
        next_page=url_for(request.endpoint, page=users.next_num, **args),
        q=q,
        field=field,
        brackets=brackets
    )


@admin.route("/admin/users/new")
@admins_only
def users_new():
    return render_template("admin/users/new.html")


@admin.route("/admin/users/<int:user_id>")
@admins_only
def users_detail(user_id):
    # Get user object
    user = Users.query.filter_by(id=user_id).first_or_404()

    # Get the user's solves
    solves = user.get_solves(admin=True)

    # Get challenges that the user is missing
    if get_config("user_mode") == TEAMS_MODE:
        if user.team:
            all_solves = user.team.get_solves(admin=True)
        else:
            all_solves = user.get_solves(admin=True)
    else:
        all_solves = user.get_solves(admin=True)

    solve_ids = [s.challenge_id for s in all_solves]
    missing = Challenges.query.filter(not_(Challenges.id.in_(solve_ids))).all()

    # Get IP addresses that the User has used
    addrs = (
        Tracking.query.filter_by(user_id=user_id).order_by(Tracking.date.desc()).all()
    )

    # Get Fails
    fails = user.get_fails(admin=True)

    # Get Awards
    awards = user.get_awards(admin=True)

    # Check if the user has an account (team or user)
    # so that we don't throw an error if they dont
    if user.account:
        score = user.account.get_score(admin=True)
        place = user.account.get_place(admin=True)
    else:
        score = None
        place = None

    return render_template(
        "admin/users/user.html",
        solves=solves,
        user=user,
        addrs=addrs,
        score=score,
        missing=missing,
        place=place,
        fails=fails,
        awards=awards,
    )
