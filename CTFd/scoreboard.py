from flask import render_template, jsonify, Blueprint, redirect, url_for, request
from sqlalchemy.sql.expression import union_all

from CTFd.models import db, Teams, Solves, Awards, Challenges
from CTFd.utils import config
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils import get_config
from CTFd.utils import user as current_user

from CTFd.utils.scores import get_standings, get_user_standings, get_team_standings

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_view():
    if get_config('view_scoreboard_if_authed') and not config.authed():
        return redirect(url_for('auth.login', next=request.path))
    if config.hide_scores():
        return render_template('scoreboard.html', errors=['Scores are currently hidden'])
    standings = get_team_standings()
    return render_template('scoreboard.html', teams=standings, score_frozen=config.is_scoreboard_frozen())


@scoreboard.route('/scores')
def scores():
    # TODO: Move this to the API
    json = {'standings': []}
    if get_config('view_scoreboard_if_authed') and not config.authed():
        return redirect(url_for('auth.login', next=request.path))
    if config.hide_scores():
        return jsonify(json)

    standings = get_team_standings()

    for i, x in enumerate(standings):
        json['standings'].append({'pos': i + 1, 'id': x.team_id, 'team': x.name, 'score': int(x.score)})
    return jsonify(json)


@scoreboard.route('/top/<int:count>')
def top(count):
    # TODO: Move this to the API
    json = {'places': {}}
    if get_config('view_scoreboard_if_authed') and not current_user.authed():
        return redirect(url_for('auth.login', next=request.path))
    if config.hide_scores():
        return jsonify(json)

    if count > 20 or count < 0:
        count = 10

    standings = get_standings(count=count)

    team_ids = [team.team_id for team in standings]

    solves = Solves.query.filter(Solves.team_id.in_(team_ids))
    awards = Awards.query.filter(Awards.team_id.in_(team_ids))

    freeze = get_config('freeze')

    if freeze:
        solves = solves.filter(Solves.date < unix_time_to_utc(freeze))
        awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

    solves = solves.all()
    awards = awards.all()

    for i, team in enumerate(team_ids):
        json['places'][i + 1] = {
            'id': standings[i].team_id,
            'name': standings[i].name,
            'solves': []
        }
        for solve in solves:
            if solve.team_id == team:
                json['places'][i + 1]['solves'].append({
                    'chal': solve.challenge_id,
                    'team': solve.team_id,
                    'value': solve.challenge.value,
                    'time': unix_time(solve.date)
                })
        for award in awards:
            if award.team_id == team:
                json['places'][i + 1]['solves'].append({
                    'chal': None,
                    'team': award.team_id,
                    'value': award.value,
                    'time': unix_time(award.date)
                })
        json['places'][i + 1]['solves'] = sorted(json['places'][i + 1]['solves'], key=lambda k: k['time'])

    return jsonify(json)
