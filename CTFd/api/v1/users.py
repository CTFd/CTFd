from flask import session
from flask_restplus import Namespace, Resource
from CTFd.models import db, Users


users_namespace = Namespace('users', description="Endpoint to retrieve Users")


@users_namespace.route('')
class UserList(Resource):
    def get(self):
        users = Users.query.filter_by(banned=False)
        response = [user.get_dict() for user in users]
        return response
