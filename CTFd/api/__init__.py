from flask import Blueprint
from flask_restplus import Api
from CTFd.api.v1.challenges import challenges_namespace
from CTFd.api.v1.teams import teams_namespace
from CTFd.api.v1.users import users_namespace

api = Blueprint('api', __name__, url_prefix='/api/v1')
CTFd_API_v1 = Api(api, version='v1')

CTFd_API_v1.add_namespace(challenges_namespace, '/challenges')
CTFd_API_v1.add_namespace(teams_namespace, '/teams')
CTFd_API_v1.add_namespace(users_namespace, '/users')
