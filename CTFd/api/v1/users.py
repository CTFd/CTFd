from flask import request, abort
from flask_restplus import Namespace, Resource
from CTFd.models import db, Users, Solves, Awards, Fails, Tracking, Unlocks, Submissions, Notifications
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    authed
)
from CTFd.cache import cache, clear_standings
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.decorators.visibility import check_account_visibility, check_score_visibility

from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    registration_visible,
    scores_visible
)

from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.users import UserSchema


users_namespace = Namespace('users', description="Endpoint to retrieve Users")


@users_namespace.route('')
class UserList(Resource):
    @check_account_visibility
    def get(self):
        users = Users.query.filter_by(banned=False)
        response = UserSchema(view='user', many=True).dump(users)

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
        schema = UserSchema('admin')
        response = schema.load(req)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.add(response.data)
        db.session.commit()

        clear_standings()

        response = schema.dump(response.data)

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<int:user_id>')
@users_namespace.param('user_id', "User ID")
class UserPublic(Resource):
    @check_account_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        response = UserSchema('self').dump(user)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        response.data['place'] = user.place
        response.data['score'] = user.score

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()
        data = request.get_json()
        data['id'] = user_id
        schema = UserSchema(view='admin', instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()

        response = schema.dump(response.data)

        db.session.close()

        clear_standings()

        return {
            'success': True,
            'data': response
        }

    @admins_only
    def delete(self, user_id):
        Notifications.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Unlocks.query.filter_by(user_id=user_id).delete()
        Submissions.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
        db.session.close()

        clear_standings()

        return {
            'success': True
        }


@users_namespace.route('/me')
class UserPrivate(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        response = UserSchema('self').dump(user).data
        response['place'] = user.place
        response['score'] = user.score
        return {
            'success': True,
            'data': response
        }

    @authed_only
    def patch(self):
        user = get_current_user()
        data = request.get_json()
        schema = UserSchema(view='self', instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<user_id>/solves')
@users_namespace.param('user_id', "User ID or 'me'")
class UserSolves(Resource):
    def get(self, user_id):
        if user_id == 'me':
            if not authed():
                abort(403)
            user = get_current_user()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            user = Users.query.filter_by(id=user_id).first_or_404()

        solves = user.get_solves(
            admin=is_admin()
        )
        for solve in solves:
            setattr(solve, 'value', 100)

        view = 'user' if not is_admin() else 'admin'
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@users_namespace.route('/<user_id>/fails')
@users_namespace.param('user_id', "User ID or 'me'")
class UserFails(Resource):
    def get(self, user_id):
        if user_id == 'me':
            if not authed():
                abort(403)
            user = get_current_user()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            user = Users.query.filter_by(id=user_id).first_or_404()

        fails = user.get_fails(
            admin=is_admin()
        )

        view = 'user' if not is_admin() else 'admin'
        response = SubmissionSchema(view=view, many=True).dump(fails)
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


@users_namespace.route('/<user_id>/awards')
@users_namespace.param('user_id', "User ID or 'me'")
class UserAwards(Resource):
    def get(self, user_id):
        if user_id == 'me':
            if not authed():
                abort(403)
            user = get_current_user()
        else:
            if accounts_visible() is False or scores_visible() is False:
                abort(404)
            user = Users.query.filter_by(id=user_id).first_or_404()

        awards = user.get_awards(
            admin=is_admin()
        )

        view = 'user' if not is_admin() else 'admin'
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }
