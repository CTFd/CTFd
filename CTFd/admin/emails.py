from flask import render_template

from CTFd.admin import admin
from CTFd.utils.decorators import admins_only


@admin.route("/admin/emails", methods=["GET", "POST"])
@admins_only
def emails():
    return render_template("admin/emails.html")
