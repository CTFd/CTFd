from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import cache, config
from CTFd.utils.decorators import admins_only
from CTFd.utils.updates import update_check
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Config

from CTFd.admin import admin


@admin.route('/admin/statistics', methods=['GET'])
@admins_only
def admin_stats():
    update_check()
    teams_registered = db.session.query(db.func.count(Teams.id)).first()[0]

    wrong_count = Fails.query.join(Teams, Fails.team_id == Teams.id).filter(Teams.banned == False).count()
    solve_count = Solves.query.join(Teams, Solves.team_id == Teams.id).filter(Teams.banned == False).count()

    challenge_count = db.session.query(db.func.count(Challenges.id)).first()[0]
    ip_count = db.session.query(db.func.count(Tracking.ip.distinct())).first()[0]

    solves_sub = db.session.query(Solves.challenge_id, db.func.count(Solves.challenge_id).label('solves_cnt')) \
                           .join(Teams, Solves.team_id == Teams.id).filter(Teams.banned == False) \
                           .group_by(Solves.challenge_id).subquery()
    solves = db.session.query(solves_sub.columns.challenge_id, solves_sub.columns.solves_cnt, Challenges.name) \
                       .join(Challenges, solves_sub.columns.challenge_id == Challenges.id).all()
    solve_data = {}
    for chal, count, name in solves:
        solve_data[name] = count

    most_solved = None
    least_solved = None
    if len(solve_data):
        most_solved = max(solve_data, key=solve_data.get)
        least_solved = min(solve_data, key=solve_data.get)

    db.session.expunge_all()
    db.session.commit()
    db.session.close()

    return render_template(
        'admin/statistics.html',
        team_count=teams_registered,
        ip_count=ip_count,
        wrong_count=wrong_count,
        solve_count=solve_count,
        challenge_count=challenge_count,
        solve_data=solve_data,
        most_solved=most_solved,
        least_solved=least_solved
    )

