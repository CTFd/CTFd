from flask import current_app as app, session, render_template, jsonify
from CTFd.utils import unix_time
from CTFd.models import db, Teams, Solves, Challenges

def init_scoreboard(app):
    @app.route('/scoreboard')
    def scoreboard():
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
        db.session.close()
        return render_template('scoreboard.html', teams=teams)

    @app.route('/scores')
    def scores():
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
        db.session.close()
        json = {'teams':[]}
        for i, x in enumerate(teams):
            json['teams'].append({'place':i+1, 'id':x.teamid, 'name':x.name,'score':int(x.score)})
        return jsonify(json)

    @app.route('/top/<count>')
    def topteams(count):
        try:
            count = int(count)
        except:
            count = 10
        if count > 20 or count < 0:
            count = 10

        json = {'scores':{}}

        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest).limit(count)

        for team in teams:
            solves = Solves.query.filter_by(teamid=team.teamid).all()
            json['scores'][team.name] = []
            for x in solves:
                json['scores'][team.name].append({'id':x.teamid, 'chal':x.chalid, 'team':x.teamid, 'value': x.chal.value, 'time':unix_time(x.date)})

        return jsonify(json)
