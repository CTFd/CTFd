from flask import session
from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from sqlalchemy.sql import or_

teams_namespace = Namespace('teams', description="Endpoint to retrieve Teams")


@teams_namespace.route('')
class TeamList(Resource):
    def get(self):
        teams = Teams.query.filter_by(banned=False)
        response = [team.get_dict() for team in teams]
        return response
