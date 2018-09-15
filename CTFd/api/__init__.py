from flask import Blueprint
from flask_restplus import Api
from CTFd.api.v1.challenges import challenges_namespace

from CTFd.api.v1.teams import teams_namespace
from CTFd.api.v1.users import users_namespace
from CTFd.api.v1.scoreboard import scoreboard_namespace
from CTFd.api.v1.statistics import statistics_namespace

api = Blueprint('api', __name__, url_prefix='/api/v1')
CTFd_API_v1 = Api(api, version='v1')

CTFd_API_v1.add_namespace(challenges_namespace, '/challenges')
CTFd_API_v1.add_namespace(scoreboard_namespace, '/scoreboard')
CTFd_API_v1.add_namespace(teams_namespace, '/teams')
CTFd_API_v1.add_namespace(users_namespace, '/users')
CTFd_API_v1.add_namespace(statistics_namespace, '/statistics')