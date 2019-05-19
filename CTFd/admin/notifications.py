from flask import render_template
from CTFd.utils.decorators import admins_only
from CTFd.models import Notifications
from CTFd.admin import admin


@admin.route("/admin/notifications")
@admins_only
def notifications():
    notifs = Notifications.query.order_by(Notifications.id.desc()).all()
    return render_template("admin/notifications.html", notifications=notifs)
