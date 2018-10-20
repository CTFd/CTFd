from flask import current_app as app, render_template, request, redirect, abort, jsonify, url_for, session, Blueprint, \
    Response, send_file
from flask.helpers import safe_join
from passlib.hash import bcrypt_sha256

from CTFd.models import db, Users, Teams, Solves, Awards, Files, Pages, Tracking
from CTFd.utils.decorators import authed_only
from CTFd.utils import markdown
from CTFd.cache import cache
from CTFd.utils import get_config, set_config
from CTFd.utils.user import get_current_user, authed, get_ip
from CTFd.utils import config
from CTFd.utils.config.pages import get_page
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils import user as current_user
from CTFd.utils.dates import ctf_ended, ctf_paused, ctf_started, ctftime, unix_time_to_utc
from CTFd.utils import validators
from CTFd.utils.crypto import verify_password

import os

teams = Blueprint('teams', __name__)


@teams.route('/teams', defaults={'page': '1'})
def list(page):
    page = request.args.get('page', 1)
    if get_config('workshop_mode'):
        abort(404)
    page = abs(int(page))
    results_per_page = 50
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page

    # TODO: Should teams confirm emails?
    # if get_config('verify_emails'):
    #     count = Teams.query.filter_by(verified=True, banned=False).count()
    #     teams = Teams.query.filter_by(verified=True, banned=False).slice(page_start, page_end).all()
    # else:
    count = Teams.query.filter_by(banned=False).count()
    teams = Teams.query.filter_by(banned=False).slice(page_start, page_end).all()

    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('teams/teams.html', teams=teams, team_pages=pages, curr_page=page)


@teams.route('/teams/join', methods=['GET', 'POST'])
@authed_only
def join():
    if request.method == 'GET':
        return render_template('teams/join_team.html')
    if request.method == 'POST':
        teamname = request.form.get('name')
        passphrase = request.form.get('password', '').strip()

        team = Teams.query.filter_by(name=teamname).first()
        user = get_current_user()
        if team and verify_password(passphrase, team.password):
            user.team_id = team.id
            db.session.commit()
            return redirect(url_for('challenges.challenges_view'))
        else:
            errors = ['That information is incorrect']
            return render_template('teams/join_team.html', errors=errors)


@teams.route('/teams/new', methods=['GET', 'POST'])
@authed_only
def new():
    if request.method == 'GET':
        return render_template("teams/new_team.html")
    elif request.method == 'POST':
        teamname = request.form.get('name')
        passphrase = request.form.get('password', '').strip()

        user = get_current_user()

        team = Teams(
            name=teamname,
            password=passphrase
        )

        db.session.add(team)
        db.session.commit()

        user.team_id = team.id
        db.session.commit()
        return redirect(url_for('challenges.challenges_view'))


@teams.route('/team', methods=['GET'])
@authed_only
def private():
    user = get_current_user()
    if not user.team_id:
        return render_template(
            'teams/team_enrollment.html',
        )

    team_id = user.team_id

    freeze = get_config('freeze')
    team = Teams.query.filter_by(id=team_id).first_or_404()
    solves = Solves.query.filter_by(team_id=team_id)
    awards = Awards.query.filter_by(team_id=team_id)

    place = team.place
    score = team.score

    if freeze:
        freeze = unix_time_to_utc(freeze)
        if team_id != session.get('id'):
            solves = solves.filter(Solves.date < freeze)
            awards = awards.filter(Awards.date < freeze)

    solves = solves.all()
    awards = awards.all()

    return render_template(
        'teams/team.html',
        solves=solves,
        awards=awards,
        team=team,
        score=score,
        place=place,
        score_frozen=config.is_scoreboard_frozen()
    )


@teams.route('/teams/<int:team_id>', methods=['GET', 'POST'])
def public(team_id):
    if get_config('workshop_mode'):
        abort(404)

    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    errors = []
    freeze = get_config('freeze')
    team = Teams.query.filter_by(id=team_id).first_or_404()
    solves = Solves.query.filter_by(team_id=team_id)
    awards = Awards.query.filter_by(team_id=team_id)

    place = team.place
    score = team.score

    if freeze:
        freeze = unix_time_to_utc(freeze)
        if team_id != session.get('id'):
            solves = solves.filter(Solves.date < freeze)
            awards = awards.filter(Awards.date < freeze)

    solves = solves.all()
    awards = awards.all()

    if config.hide_scores() and team_id != session.get('id'):
        errors.append('Scores are currently hidden')

    if errors:
        return render_template('teams/team.html', team=team, errors=errors)

    if request.method == 'GET':
        return render_template(
            'teams/team.html',
            solves=solves,
            awards=awards,
            team=team,
            score=score,
            place=place,
            score_frozen=config.is_scoreboard_frozen()
        )
    # TODO: Move this to /api/team/<id>.json
    # elif request.method == 'POST':
    #     json = {'solves': []}
    #     for x in solves:
    #         json['solves'].append({'id': x.id, 'chal': x.chalid, 'team': x.team_id})
    #     return jsonify(json)