from flask import session, abort
from flask_restplus import Namespace, Resource
from CTFd.models import db, Users, Solves, Awards, Fails
from CTFd.utils.decorators import authed_only
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils.user import get_current_user
from CTFd.utils import get_config


users_namespace = Namespace('users', description="Endpoint to retrieve Users")


@users_namespace.route('')
class UserList(Resource):
    def get(self):
        users = Users.query.filter_by(banned=False)
        response = [user.get_dict() for user in users]
        return response


@users_namespace.route('/<user_id>')
@users_namespace.param('user_id', "User ID or 'me'")
class User(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        response = user.get_dict()
        response['place'] = user.place
        response['score'] = user.score
        return response


@users_namespace.route('/<user_id>/solves')
@users_namespace.param('user_id', "User ID or 'me'")
class UserSolves(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        solves = Solves.query.filter_by(user_id=user.id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if user_id != session.get('id'):
                solves = solves.filter(Solves.date < freeze)

        response = [solve.get_dict() for solve in solves.all()]
        return response


@users_namespace.route('/<user_id>/fails')
@users_namespace.param('user_id', "User ID or 'me'")
class UserFails(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        fails = Fails.query.filter_by(user_id=user.id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if user_id != session.get('id'):
                fails = fails.filter(Solves.date < freeze)

        response = [fail.get_dict() for fail in fails.all()]
        return response


@users_namespace.route('/<user_id>/awards')
@users_namespace.param('user_id', "User ID or 'me'")
class UserAwards(Resource):
    def get(self, user_id):
        if user_id == 'me':
            user = get_current_user()
        else:
            user = Users.query.filter_by(id=user_id).first_or_404()

        awards = Awards.query.filter_by(user_id=user.id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if user_id != session.get('id'):
                awards = awards.filter(Awards.date < freeze)

        response = [award.get_dict() for award in awards.all()]
        return response