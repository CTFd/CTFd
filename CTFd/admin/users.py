from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Users
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/users', defaults={'page': '1'})
@admins_only
def list(page):
    page = request.args.get('page', 1)

    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    users = Users.query.order_by(Users.id.asc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Users.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)

    return render_template('admin/users.html', users=users, pages=pages, curr_page=page)