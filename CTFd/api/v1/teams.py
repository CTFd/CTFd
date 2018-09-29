from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams, Solves, Awards, Fails
from CTFd.utils.user import get_current_team
from CTFd.utils.decorators import (
    authed_only,
    admins_only
)
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils import get_config

teams_namespace = Namespace('teams', description="Endpoint to retrieve Teams")


@teams_namespace.route('')
class TeamList(Resource):
    def get(self):
        teams = Teams.query.filter_by(banned=False)
        response = [team.get_dict() for team in teams]
        return response

    def post(self):
        req = request.get_json()
        t = Teams(**req)
        db.session.add(t)
        db.session.commit()
        return t.get_dict()


@teams_namespace.route('/<team_id>')
@teams_namespace.param('team_id', "Team ID or 'me'")
class Team(Resource):
    def get(self, team_id):
        if team_id == 'me':
            team = get_current_team()
        else:
            team = Teams.query.filter_by(id=team_id).first_or_404()

        response = team.get_dict()
        return response

    def patch(self, team_id):
        if team_id == 'me':
            team = get_current_team()
        else:
            team = Teams.query.filter_by(id=team_id).first_or_404()
        pass

    @admins_only
    def delete(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        for member in team.members:
            member.team_id = None

        db.session.delete(team)
        db.session.commit()
        db.session.close()

        response = {
            'success': True,
        }
        return response


# @teams_namespace.route('/<team_id>/ban')
# @teams_namespace.param('team_id', "Team ID")
# class TeamBans(Resource):
#     def get(self, team_id):
#         team = Teams.query.filter_by(id=team_id).first_or_404()
#         response = {
#             'banned': team.banned
#         }
#         return response
#
#     def put(self, team_id):
#         team = Teams.query.filter_by(id=team_id).first_or_404()
#         team.banned = True
#         db.session.commit()
#         response = {
#             'banned': team.banned
#         }
#         return response
#
#     def delete(self, team_id):
#         team = Teams.query.filter_by(id=team_id).first_or_404()
#         team.banned = False
#         db.session.commit()
#         response = {
#             'banned': team.banned
#         }
#         return response


@teams_namespace.route('/<team_id>/mail')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamMails(Resource):
    def post(self, team_id):
        pass


@teams_namespace.route('/<team_id>/solves')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamSolves(Resource):
    def get(self, team_id):
        if team_id == 'me':
            team = get_current_team()
        else:
            team = Teams.query.filter_by(id=team_id).first_or_404()

        solves = Solves.query.filter_by(team_id=team_id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if team_id != session.get('team_id'):
                solves = solves.filter(Solves.date < freeze)

        response = [solve.get_dict() for solve in solves.all()]
        return response


@teams_namespace.route('/<team_id>/fails')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamFails(Resource):
    def get(self, team_id):
        if team_id == 'me':
            team = get_current_team()
        else:
            team = Teams.query.filter_by(id=team_id).first_or_404()

        fails = Fails.query.filter_by(team_id=team_id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if team_id != session.get('team_id'):
                fails = fails.filter(Solves.date < freeze)

        response = [fail.get_dict() for fail in fails.all()]
        return response


@teams_namespace.route('/<team_id>/awards')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamAwards(Resource):
    def get(self, team_id):
        if team_id == 'me':
            team = get_current_team()
        else:
            team = Teams.query.filter_by(id=team_id).first_or_404()

        awards = Awards.query.filter_by(team_id=team_id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if team_id != session.get('team_id'):
                awards = awards.filter(Awards.date < freeze)

        response = [award.get_dict() for award in awards.all()]
        return response