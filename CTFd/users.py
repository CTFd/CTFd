from flask import request, render_template, Blueprint

from CTFd.models import Users
from CTFd.utils.decorators import authed_only
from CTFd.utils import config
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)

users = Blueprint("users", __name__)


@users.route("/users")
@check_account_visibility
def listing():
    page = abs(request.args.get("page", 1, type=int))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    count = Users.query.filter_by(banned=False, hidden=False).count()
    users = (
        Users.query.filter_by(banned=False, hidden=False)
        .slice(page_start, page_end)
        .all()
    )

    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template("users/users.html", users=users, pages=pages, curr_page=page)


@users.route("/profile")
@users.route("/user")
@authed_only
def private():
    user = get_current_user()

    solves = user.get_solves()
    awards = user.get_awards()

    place = user.place
    score = user.score

    return render_template(
        "users/private.html",
        solves=solves,
        awards=awards,
        user=user,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen(),
    )


@users.route("/users/<int:user_id>")
@check_account_visibility
@check_score_visibility
def public(user_id):
    user = Users.query.filter_by(id=user_id, banned=False, hidden=False).first_or_404()
    return render_template("users/public.html", user=user)
