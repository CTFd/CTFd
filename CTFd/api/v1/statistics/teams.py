from flask_restplus import Namespace, Resource
from CTFd.models import db, Teams
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.decorators import (
    admins_only,
)
from CTFd.api.v1.statistics import statistics_namespace


@statistics_namespace.route('/teams')
class TeamStatistics(Resource):
    @admins_only
    def get(self):
        registered = Teams.query.count()
        data = {
            'registered': registered,
        }
        return {
            'success': True,
            'data': data
        }
