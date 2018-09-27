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


@admin.route('/admin/wrong_keys', defaults={'page': '1'}, methods=['GET'])
@admin.route('/admin/wrong_keys/<int:page>', methods=['GET'])
@admins_only
def admin_wrong_key(page):
    # TODO: Convert to submissions. Perhaps only a single page.
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    wrong_keys = Fails.query.add_columns(Fails.id, Fails.challenge_id, Fails.flag, Fails.team_id, Fails.date,
                                             Challenges.name.label('chal_name'), Teams.name.label('team_name')) \
        .join(Challenges) \
        .join(Teams) \
        .order_by(Fails.date.desc()) \
        .slice(page_start, page_end) \
        .all()

    wrong_count = db.session.query(db.func.count(Fails.id)).first()[0]
    pages = int(wrong_count / results_per_page) + (wrong_count % results_per_page > 0)

    return render_template('admin/wrong_keys.html', wrong_keys=wrong_keys, pages=pages, curr_page=page)


@admin.route('/admin/correct_keys', defaults={'page': '1'}, methods=['GET'])
@admin.route('/admin/correct_keys/<int:page>', methods=['GET'])
@admins_only
def admin_correct_key(page):
    # TODO: Convert to submissions. Perhaps only a single page.
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    solves = Solves.query.add_columns(Solves.id, Solves.challenge_id, Solves.team_id, Solves.date, Solves.flag,
                                      Challenges.name.label('chal_name'), Teams.name.label('team_name')) \
        .join(Challenges) \
        .join(Teams) \
        .order_by(Solves.date.desc()) \
        .slice(page_start, page_end) \
        .all()

    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    pages = int(solve_count / results_per_page) + (solve_count % results_per_page > 0)

    return render_template('admin/correct_keys.html', solves=solves, pages=pages, curr_page=page)
