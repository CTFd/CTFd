from flask import session
from flask_restplus import Namespace, Resource

from CTFd.models import Solves, Awards
from CTFd.utils.scores import get_standings
from CTFd.utils import get_config
from CTFd.utils.dates import unix_time_to_utc, unix_time

scoreboard_namespace = Namespace('scoreboard', description="Endpoint to retrieve scores")


@scoreboard_namespace.route('')
class ScoreboardList(Resource):
    def get(self):
        standings = get_standings()
        response = []

        for i, x in enumerate(standings):
            response.append(
                {
                    'pos': i + 1,
                    'id': x.team_id,
                    'team': x.name,
                    'score': int(x.score)
                }
            )
        return response


@scoreboard_namespace.route('/top/<count>')
@scoreboard_namespace.param('count', 'How many top teams to return')
class ScoreboardList(Resource):
    def get(self, count):
        response = {}

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
            response[i + 1] = {
                'id': standings[i].team_id,
                'name': standings[i].name,
                'solves': []
            }
            for solve in solves:
                if solve.team_id == team:
                    response[i + 1]['solves'].append({
                        'chal': solve.challenge_id,
                        'team': solve.team_id,
                        'value': solve.challenge.value,
                        'time': unix_time(solve.date)
                    })
            for award in awards:
                if award.team_id == team:
                    response[i + 1]['solves'].append({
                        'chal': None,
                        'team': award.team_id,
                        'value': award.value,
                        'time': unix_time(award.date)
                    })
            response[i + 1]['solves'] = sorted(response[i + 1]['solves'], key=lambda k: k['time'])

        return response
