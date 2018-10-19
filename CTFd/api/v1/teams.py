from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams, Solves, Awards, Fails
from CTFd.schemas.teams import TeamSchema
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.awards import AwardSchema
from CTFd.utils.user import (
    get_current_team,
    is_admin
)
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
)
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils import get_config

teams_namespace = Namespace('teams', description="Endpoint to retrieve Teams")


@teams_namespace.route('')
class TeamList(Resource):
    def get(self):
        teams = Teams.query.filter_by(banned=False)
        view = list(TeamSchema.views.get(session.get('type')))
        view.remove('members')
        response = TeamSchema(view=view, many=True).dump(teams)
        return response.data

    def post(self):
        req = request.get_json()
        view = TeamSchema.views.get(session.get('type', 'self'))
        schema = TeamSchema(view=view)
        team = schema.load(req)
        if team.errors:
            return team.errors
        db.session.add(team.data)
        db.session.commit()
        return schema.dump(team.data)


@teams_namespace.route('/<team_id>')
@teams_namespace.param('team_id', "Team ID")
class TeamPublic(Resource):
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        view = TeamSchema.views.get(session.get('type'))
        response = TeamSchema(view=view).dump(team)
        return response

    @admins_only
    def patch(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()
        data = request.get_json()
        data['id'] = team_id
        response = TeamSchema(view='admin', instance=team, partial=True).load(data)
        if response.errors:
            return response.errors

        db.session.commit()
        response = TeamSchema('admin').dump(response.data)
        db.session.close()
        return response

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
            'message': ''
        }
        return response


@teams_namespace.route('/me')
@teams_namespace.param('team_id', "Current Team")
class TeamPrivate(Resource):
    @authed_only
    def get(self):
        team = get_current_team()
        response = TeamSchema(view='self').dump(team)
        return response

    @authed_only
    def patch(self):
        team = get_current_team()
        data = request.get_json()
        response = TeamSchema(view='self', instance=team, partial=True).load(data)
        if response.errors:
            return response.errors

        db.session.commit()
        response = TeamSchema('self').dump(response.data)
        db.session.close()
        return response


# @teams_namespace.route('/<team_id>/mail')
# @teams_namespace.param('team_id', "Team ID or 'me'")
# class TeamMails(Resource):
#     def post(self, team_id):
#         pass


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

        view = 'admin' if is_admin() else 'user'

        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(solves.all()).data
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

        view = 'admin' if is_admin() else 'user'

        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(fails.all()).data
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

        schema = SubmissionSchema(many=True)
        response = schema.dump(awards.all()).data
        return response
