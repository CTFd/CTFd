from flask import render_template
from CTFd.utils.decorators import admins_only
from CTFd.utils.updates import update_check
from CTFd.utils.modes import get_model
from CTFd.models import db, Notifications
from CTFd.admin import admin


@admin.route('/admin/notifications')
@admins_only
def notifications():
    notifs = Notifications.query.order_by(Notifications.id.desc()).all()
    return render_template('admin/notifications.html', notifications=notifs)
