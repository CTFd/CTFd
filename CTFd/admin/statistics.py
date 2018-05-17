from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache, update_check
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError

from CTFd import utils

admin_statistics = Blueprint('admin_statistics', __name__)


@admin_statistics.route('/admin/graphs/<graph_type>')
@admins_only
def admin_graph(graph_type):
    if graph_type == 'categories':
        categories = db.session.query(Challenges.category, db.func.count(Challenges.category)).group_by(Challenges.category).all()
        json_data = {'categories': []}
        for category, count in categories:
            json_data['categories'].append({'category': category, 'count': count})
        return jsonify(json_data)
    elif graph_type == "solves":
        solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves_cnt')) \
                               .join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False) \
                               .group_by(Solves.chalid).subquery()
        solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves_cnt, Challenges.name) \
                           .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
        json_data = {}
        for chal, count, name in solves:
            json_data[name] = count
        return jsonify(json_data)
    elif graph_type == "solve-percentages":
        chals = Challenges.query.add_columns('id', 'name', 'hidden', 'max_attempts').order_by(Challenges.value).all()

        teams_with_points = db.session.query(Solves.teamid)\
            .join(Teams)\
            .filter(Teams.banned == False)\
            .group_by(Solves.teamid)\
            .count()

        percentage_data = []
        for x in chals:
            solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id)\
                .filter(Solves.chalid == x[1], Teams.banned == False)\
                .count()

            if teams_with_points > 0:
                percentage = (float(solve_count) / float(teams_with_points))
            else:
                percentage = 0.0

            percentage_data.append({
                'id': x.id,
                'name': x.name,
                'percentage': percentage,
            })

        percentage_data = sorted(percentage_data, key=lambda x: x['percentage'], reverse=True)
        json_data = {'percentages': percentage_data}
        return jsonify(json_data)


@admin_statistics.route('/admin/statistics', methods=['GET'])
@admins_only
def admin_stats():
    update_check()
    teams_registered = db.session.query(db.func.count(Teams.id)).first()[0]

    wrong_count = WrongKeys.query.join(Teams, WrongKeys.teamid == Teams.id).filter(Teams.banned == False).count()
    solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False).count()

    challenge_count = db.session.query(db.func.count(Challenges.id)).first()[0]
    ip_count = db.session.query(db.func.count(Tracking.ip.distinct())).first()[0]

    solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves_cnt')) \
                           .join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False) \
                           .group_by(Solves.chalid).subquery()
    solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves_cnt, Challenges.name) \
                       .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
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


@admin_statistics.route('/admin/wrong_keys', defaults={'page': '1'}, methods=['GET'])
@admin_statistics.route('/admin/wrong_keys/<int:page>', methods=['GET'])
@admins_only
def admin_wrong_key(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    wrong_keys = WrongKeys.query.add_columns(WrongKeys.id, WrongKeys.chalid, WrongKeys.flag, WrongKeys.teamid, WrongKeys.date,
                                             Challenges.name.label('chal_name'), Teams.name.label('team_name')) \
        .join(Challenges) \
        .join(Teams) \
        .order_by(WrongKeys.date.desc()) \
        .slice(page_start, page_end) \
        .all()

    wrong_count = db.session.query(db.func.count(WrongKeys.id)).first()[0]
    pages = int(wrong_count / results_per_page) + (wrong_count % results_per_page > 0)

    return render_template('admin/wrong_keys.html', wrong_keys=wrong_keys, pages=pages, curr_page=page)


@admin_statistics.route('/admin/correct_keys', defaults={'page': '1'}, methods=['GET'])
@admin_statistics.route('/admin/correct_keys/<int:page>', methods=['GET'])
@admins_only
def admin_correct_key(page):
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    solves = Solves.query.add_columns(Solves.id, Solves.chalid, Solves.teamid, Solves.date, Solves.flag,
                                      Challenges.name.label('chal_name'), Teams.name.label('team_name')) \
        .join(Challenges) \
        .join(Teams) \
        .order_by(Solves.date.desc()) \
        .slice(page_start, page_end) \
        .all()

    solve_count = db.session.query(db.func.count(Solves.id)).first()[0]
    pages = int(solve_count / results_per_page) + (solve_count % results_per_page > 0)

    return render_template('admin/correct_keys.html', solves=solves, pages=pages, curr_page=page)
