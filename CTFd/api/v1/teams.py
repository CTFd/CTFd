from flask import session, request, abort
from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams, Solves, Awards, Fails
from CTFd.schemas.teams import TeamSchema
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.awards import AwardSchema
from CTFd.cache import cache, clear_standings
from CTFd.utils.decorators.visibility import check_account_visibility, check_score_visibility
from CTFd.utils.config.visibility import (
    accounts_visible,
    scores_visible
)
from CTFd.utils.user import (
    get_current_team,
    is_admin,
    authed
)
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
)
import copy

teams_namespace = Namespace('teams', description="Endpoint to retrieve Teams")


@teams_namespace.route('')
class TeamList(Resource):
    @check_account_visibility
    def get(self):
        teams = Teams.query.filter_by(hidden=False, banned=False)
        view = copy.deepcopy(TeamSchema.views.get(
            session.get('type', 'user')
        ))
        view.remove('members')
        response = TeamSchema(view=view, many=True).dump(teams)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def post(self):
        req = request.get_json()
        view = TeamSchema.views.get(session.get('type', 'self'))
        schema = TeamSchema(view=view)
        response = schema.load(req)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()

        return {
            'success': True,
            'data': response.data
        }


@teams_namespace.route('/<int:team_id>')
@teams_namespace.param('team_id', "Team ID")
class TeamPublic(Resource):
    @check_account_visibility
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        view = TeamSchema.views.get(session.get('type', 'user'))
        schema = TeamSchema(view=view)
        response = schema.dump(team)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()
        data = request.get_json()
        data['id'] = team_id

        schema = TeamSchema(view='admin', instance=team, partial=True)

        response = schema.load(data)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        response = schema.dump(response.data)
        db.session.commit()
        db.session.close()

        clear_standings()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        for member in team.members:
            member.team_id = None

        db.session.delete(team)
        db.session.commit()
        db.session.close()

        clear_standings()

        return {
            'success': True,
        }


@teams_namespace.route('/me')
@teams_namespace.param('team_id', "Current Team")
class TeamPrivate(Resource):
    @authed_only
    def get(self):
        team = get_current_team()
        response = TeamSchema(view='self').dump(team)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @authed_only
    def patch(self):
        team = get_current_team()
        data = request.get_json()

        response = TeamSchema(view='self', instance=team, partial=True).load(data)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()

        response = TeamSchema('self').dump(response.data)
        db.session.close()

        return {
            'success': True,
            'data': response.data
        }


@teams_namespace.route('/<team_id>/solves')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamSolves(Resource):

    def get(self, team_id):
        if team_id == 'me':
            if not authed():
                abort(403)
            team = get_current_team()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            team = Teams.query.filter_by(id=team_id).first_or_404()

        solves = team.get_solves(
            admin=is_admin()
        )

        view = 'admin' if is_admin() else 'user'
        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(solves)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@teams_namespace.route('/<team_id>/fails')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamFails(Resource):

    def get(self, team_id):
        if team_id == 'me':
            if not authed():
                abort(403)
            team = get_current_team()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            team = Teams.query.filter_by(id=team_id).first_or_404()

        fails = team.get_fails(
            admin=is_admin()
        )

        view = 'admin' if is_admin() else 'user'

        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(fails)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        if is_admin():
            data = response.data
        else:
            data = []
        count = len(response.data)

        return {
            'success': True,
            'data': data,
            'meta': {
                'count': count
            }
        }


@teams_namespace.route('/<team_id>/awards')
@teams_namespace.param('team_id', "Team ID or 'me'")
class TeamAwards(Resource):

    def get(self, team_id):
        if team_id == 'me':
            if not authed():
                abort(403)
            team = get_current_team()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            team = Teams.query.filter_by(id=team_id).first_or_404()

        awards = team.get_awards(
            admin=is_admin()
        )

        schema = AwardSchema(many=True)
        response = schema.dump(awards)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }
