from flask import session
from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams, Solves, Awards
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils import get_config

teams_namespace = Namespace('teams', description="Endpoint to retrieve Teams")


@teams_namespace.route('')
class TeamList(Resource):
    def get(self):
        teams = Teams.query.filter_by(banned=False)
        response = [team.get_dict() for team in teams]
        return response


@teams_namespace.route('/<team_id>')
@teams_namespace.param('team_id', 'Team ID')
class Team(Resource):
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        solves = Solves.query.filter_by(team_id=team_id)
        awards = Awards.query.filter_by(team_id=team_id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if team_id != session.get('team_id'):
                solves = solves.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        solves = [solve.get_dict() for solve in solves.all()]
        awards = [award.get_dict() for award in awards.all()]

        response = team.get_dict()
        response['place'] = team.place
        response['score'] = team.score
        response['solves'] = solves
        response['awards'] = awards
        return response
