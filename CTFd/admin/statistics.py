from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import cache, config
from CTFd.utils.decorators import admins_only
from CTFd.utils.updates import update_check
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Config

from CTFd.admin import admin


@admin.route('/admin/graphs/<graph_type>')
@admins_only
def admin_graph(graph_type):
    # TODO: Move to API
    if graph_type == 'categories':
        categories = db.session.query(Challenges.category, db.func.count(Challenges.category)).group_by(Challenges.category).all()
        json_data = {'categories': []}
        for category, count in categories:
            json_data['categories'].append({'category': category, 'count': count})
        return jsonify(json_data)
    elif graph_type == "solves":
        solves_sub = db.session.query(Solves.challenge_id, db.func.count(Solves.challenge_id).label('solves_cnt')) \
                               .join(Teams, Solves.team_id == Teams.id).filter(Teams.banned == False) \
                               .group_by(Solves.challenge_id).subquery()
        solves = db.session.query(solves_sub.columns.challenge_id, solves_sub.columns.solves_cnt, Challenges.name) \
                           .join(Challenges, solves_sub.columns.challenge_id == Challenges.id).all()
        json_data = {}
        for chal, count, name in solves:
            json_data[name] = count
        return jsonify(json_data)
    elif graph_type == "solve-percentages":
        chals = Challenges.query.add_columns('id', 'name', 'hidden', 'max_attempts').order_by(Challenges.value).all()

        teams_with_points = db.session.query(Solves.team_id)\
            .join(Teams)\
            .filter(Teams.banned == False)\
            .group_by(Solves.team_id)\
            .count()

        percentage_data = []
        for x in chals:
            solve_count = Solves.query.join(Teams, Solves.team_id == Teams.id)\
                .filter(Solves.challenge_id == x[1], Teams.banned == False)\
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
