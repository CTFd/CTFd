from flask import render_template

from CTFd.admin import admin
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only
from CTFd.utils.scores import get_standings, get_user_standings


@admin.route("/admin/scoreboard")
@admins_only
def scoreboard_listing():
    standings = get_standings(admin=True)
    user_standings = get_user_standings(admin=True) if is_teams_mode() else None
    return render_template(
        "admin/scoreboard.html", standings=standings, user_standings=user_standings
    )
