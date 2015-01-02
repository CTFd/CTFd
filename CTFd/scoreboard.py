from flask import current_app as app, session, render_template, jsonify
from CTFd.utils import unix_time
from CTFd.models import db, Teams, Solves, Challenges

def init_scoreboard(app):
    @app.route('/scoreboard')
    def scoreboard():
        score = db.func.sum(Challenges.value).label('score')
        quickest = db.func.max(Solves.date).label('quickest')
        teams = db.session.query(Solves.teamid, Teams.name, score).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), quickest)
        #teams = db.engine.execute("SELECT solves.teamid, teams.id, teams.name, SUM(value) as score, MAX(solves.date) as quickest FROM solves JOIN teams ON solves.teamid=teams.id INNER JOIN challenges ON solves.chalid=challenges.id WHERE teams.banned IS NULL GROUP BY solves.teamid ORDER BY score DESC, quickest ASC;")
        db.session.close()
        return render_template('scoreboard.html', teams=teams)

    @app.route('/scores')
    def scores():
        #teams = db.engine.execute("SELECT solves.teamid, teams.id, teams.name, SUM(value) as score, MAX(solves.date) as quickest FROM solves JOIN teams ON solves.teamid=teams.id INNER JOIN challenges ON solves.chalid=challenges.id WHERE teams.banned IS NULL GROUP BY solves.teamid ORDER BY score DESC, quickest ASC;")
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

        #teams = db.engine.execute("SELECT solves.teamid, teams.id, teams.name, SUM(value) as score, MAX(solves.date) as quickest FROM solves JOIN teams ON solves.teamid=teams.id INNER JOIN challenges ON solves.chalid=challenges.id WHERE teams.banned IS NULL GROUP BY solves.teamid ORDER BY score DESC, quickest ASC LIMIT {0};".format(count))
        score = db.func.sum(Challenges.value).label('score')
        teams = db.session.query(Solves.teamid, Teams.name, score, db.func.max(Solves.date).label('quickest')).join(Teams).join(Challenges).filter(Teams.banned == None).group_by(Solves.teamid).order_by(score.desc(), Solves.date).limit(count)


        for team in teams:
            solves = Solves.query.filter_by(teamid=team.teamid).all()
            json['scores'][team.name] = []
            for x in solves:
                json['scores'][team.name].append({'id':x.teamid, 'chal':x.chalid, 'team':x.teamid, 'value': x.chal.value, 'time':unix_time(x.date)})

        return jsonify(json)
