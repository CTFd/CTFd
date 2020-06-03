from flask import Blueprint, render_template, request

from CTFd.models import Users
from CTFd.utils import config
from CTFd.utils.decorators import authed_only
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.user import get_current_user
from CTFd.utils.helpers import get_infos, get_errors

users = Blueprint("users", __name__)


@users.route("/users")
@check_account_visibility
def listing():
    page = abs(request.args.get("page", 1, type=int))

    users = (
        Users.query.filter_by(banned=False, hidden=False)
        .order_by(Users.id.asc())
        .paginate(page=page, per_page=50)
    )

    return render_template("users/users.html", users=users)


@users.route("/profile")
@users.route("/user")
@authed_only
def private():
    infos = get_infos()
    errors = get_errors()

    user = get_current_user()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    return render_template(
        "users/private.html",
        user=user,
        account=user.account,
        infos=infos,
        errors=errors,
    )


@users.route("/users/<int:user_id>")
@check_account_visibility
@check_score_visibility
def public(user_id):
    infos = get_infos()
    errors = get_errors()
    user = Users.query.filter_by(id=user_id, banned=False, hidden=False).first_or_404()

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    return render_template(
        "users/public.html", user=user, account=user.account, infos=infos, errors=errors
    )
