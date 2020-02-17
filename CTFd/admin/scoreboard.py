from flask import render_template

from CTFd.admin import admin
from CTFd.scoreboard import get_standings
from CTFd.utils.decorators import admins_only


@admin.route("/admin/scoreboard")
@admins_only
def scoreboard_listing():
    standings = get_standings(admin=True)
    return render_template("admin/scoreboard.html", standings=standings)
