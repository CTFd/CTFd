from flask_restplus import Namespace

statistics_namespace = Namespace('statistics', description="Endpoint to retrieve Statistics")

from CTFd.api.v1.statistics import challenges
from CTFd.api.v1.statistics import teams
from CTFd.api.v1.statistics import users
from CTFd.api.v1.statistics import submissions

# TODO: Solve this cleanly.
# This is just a trick to make flake8 understand that the imports aren't unused
_ = challenges, teams, users, submissions
