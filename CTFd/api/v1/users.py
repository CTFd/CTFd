from flask import session
from flask_restplus import Namespace, Resource
from CTFd.models import db, Users, Solves, Awards
from CTFd.utils.dates import unix_time_to_utc, unix_time
from CTFd.utils import get_config


users_namespace = Namespace('users', description="Endpoint to retrieve Users")


@users_namespace.route('')
class UserList(Resource):
    def get(self):
        users = Users.query.filter_by(banned=False)
        response = [user.get_dict() for user in users]
        return response


@users_namespace.route('/<user_id>')
@users_namespace.param('user_id', 'User ID')
class User(Resource):
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        solves = Solves.query.filter_by(user_id=user_id)
        awards = Awards.query.filter_by(user_id=user_id)

        freeze = get_config('freeze')
        if freeze:
            freeze = unix_time_to_utc(freeze)
            if user_id != session.get('id'):
                solves = solves.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        solves = [solve.get_dict() for solve in solves.all()]
        awards = [award.get_dict() for award in awards.all()]

        response = user.get_dict()
        response['place'] = user.place
        response['score'] = user.score
        response['solves'] = solves
        response['awards'] = awards
        return response
