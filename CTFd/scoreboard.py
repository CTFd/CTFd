from flask import current_app as app, session, render_template, jsonify, Blueprint, redirect, url_for, request
from CTFd.utils import unix_time, authed, get_config
from CTFd.models import db, Teams, Solves, Awards, Challenges
from sqlalchemy.sql.expression import union_all

scoreboard = Blueprint('scoreboard', __name__)


@scoreboard.route('/scoreboard')
def scoreboard_view():
    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    score = db.func.sum(Challenges.value).label('score')
    scores = db.session.query(Solves.teamid.label('teamid'), Teams.name.label('name'), score, Solves.date.label('date')) \
        .join(Teams) \
        .join(Challenges) \
        .filter(Teams.banned == None) \
        .group_by(Solves.teamid)

    awards = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'),
                              db.func.sum(Awards.value).label('score'), Awards.date.label('date')) \
        .filter(Teams.id == Awards.teamid) \
        .group_by(Teams.id)

    results = union_all(scores, awards)

    standings = db.session.query(results.columns.teamid, results.columns.name,
                                 db.func.sum(results.columns.score).label('score')) \
        .group_by(results.columns.teamid) \
        .order_by(db.func.sum(results.columns.score).desc(), db.func.max(results.columns.date)) \
        .all()
    db.session.close()
    return render_template('scoreboard.html', teams=standings)


@scoreboard.route('/scores')
def scores():
    if get_config('view_scoreboard_if_authed') and not authed():
        return redirect(url_for('auth.login', next=request.path))
    score = db.func.sum(Challenges.value).label('score')
    scores = db.session.query(Solves.teamid.label('teamid'), Teams.name.label('name'), score, Solves.date.label('date')) \
        .join(Teams) \
        .join(Challenges) \
        .filter(Teams.banned == None) \
        .group_by(Solves.teamid)

    awards = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'), db.func.sum(Awards.value).label('score'), Awards.date.label('date'))\
        .filter(Teams.id==Awards.teamid)\
        .group_by(Teams.id)

    results = union_all(scores, awards)

    standings = db.session.query(results.columns.teamid, results.columns.name, db.func.sum(results.columns.score).label('score'))\
        .group_by(results.columns.teamid)\
        .order_by(db.func.sum(results.columns.score).desc(), db.func.max(results.columns.date))\
        .all()

    db.session.close()
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

    score = db.func.sum(Challenges.value).label('score')
    scores = db.session.query(Solves.teamid.label('teamid'), Teams.name.label('name'), score, Solves.date.label('date')) \
        .join(Teams) \
        .join(Challenges) \
        .filter(Teams.banned == None) \
        .group_by(Solves.teamid)

    awards = db.session.query(Teams.id.label('teamid'), Teams.name.label('name'),
                              db.func.sum(Awards.value).label('score'), Awards.date.label('date')) \
        .filter(Teams.id == Awards.teamid) \
        .group_by(Teams.id)

    results = union_all(scores, awards)

    standings = db.session.query(results.columns.teamid, results.columns.name,
                                 db.func.sum(results.columns.score).label('score')) \
        .group_by(results.columns.teamid) \
        .order_by(db.func.sum(results.columns.score).desc(), db.func.max(results.columns.date)) \
        .limit(count).all()

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
