from flask import current_app as app, session, render_template, jsonify, Blueprint, redirect, url_for, request
from CTFd.utils import unix_time, authed, get_config
from CTFd.models import db, Teams, Solves, Awards, Challenges
from sqlalchemy.sql.expression import union_all

scoreboard = Blueprint('scoreboard', __name__)

def get_standings(admin=False, count=None):
    score = db.func.sum(Challenges.value).label('score')
    date = db.func.max(Solves.date).label('date')
    scores = db.session.query(Solves.teamid.label('teamid'), score, date).join(Challenges).group_by(Solves.teamid)
    awards = db.session.query(Awards.teamid.label('teamid'), db.func.sum(Awards.value).label('score'), db.func.max(Awards.date).label('date')) \
        .group_by(Awards.teamid)
    results = union_all(scores, awards).alias('results')
    sumscores = db.session.query(results.columns.teamid, db.func.sum(results.columns.score).label('score'), db.func.max(results.columns.date).label('date')) \
        .group_by(results.columns.teamid).subquery()
    if admin:
        standings_query = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'), Teams.banned, sumscores.columns.score) \
            .join(sumscores, Teams.id == sumscores.columns.teamid) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.date)
    else:
        standings_query = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'), sumscores.columns.score) \
            .join(sumscores, Teams.id == sumscores.columns.teamid) \
            .filter(Teams.banned == False) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.date)
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()
    db.session.close()
    return standings


@scoreboard.route('/scoreboard')
def scoreboard_view():
    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    standings = get_standings()
    return render_template('scoreboard.html', teams=standings)


@scoreboard.route('/scores')
def scores():
    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    standings = get_standings()
    json = {'standings':[]}
    for i, x in enumerate(standings):
        json['standings'].append({'pos':i+1, 'id':x.teamid, 'team':x.name,'score':int(x.score)})
    return jsonify(json)


@scoreboard.route('/top/<count>')
def topteams(count):
    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    try:
        count = int(count)
    except:
        count = 10
    if count > 20 or count < 0:
        count = 10

    json = {'scores':{}}
    standings = get_standings(count=count)

    for team in standings:
        solves = Solves.query.filter_by(teamid=team.teamid).all()
        awards = Awards.query.filter_by(teamid=team.teamid).all()
        json['scores'][team.name] = []
        scores = []
        for x in solves:
            json['scores'][team.name].append({
                'chal': x.chalid,
                'team': x.teamid,
                'value': x.chal.value,
                'time': unix_time(x.date)
            })
        for award in awards:
            json['scores'][team.name].append({
                'chal': None,
                'team': award.teamid,
                'value': award.value,
                'time': unix_time(award.date)
            })
        json['scores'][team.name] = sorted(json['scores'][team.name], key=lambda k: k['time'])
    return jsonify(json)
