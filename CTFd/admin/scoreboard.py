from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.models import db, Teams, Solves, Awards, Challenges
from CTFd.utils.decorators import admins_only
from CTFd.admin import admin
from CTFd.scoreboard import get_standings


@admin.route('/admin/scoreboard')
@admins_only
def scoreboard_listing():
    standings = get_standings(admin=True)
    return render_template('admin/scoreboard.html', standings=standings)
