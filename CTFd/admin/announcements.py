from flask import render_template
from CTFd.utils.decorators import admins_only
from CTFd.utils.updates import update_check
from CTFd.utils.modes import get_model
from CTFd.models import db, Announcements
from CTFd.admin import admin


@admin.route('/admin/announcements', methods=['GET'])
@admins_only
def admin_announcements():
    announcements = Announcements.query.order_by(Announcements.id.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)