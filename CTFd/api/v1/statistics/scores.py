from flask_restx import Resource
from sqlalchemy import func

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Submissions
from CTFd.utils.decorators import admins_only


@statistics_namespace.route("/scores/distribution")
class ScoresDistribution(Resource):
    @admins_only
    def get(self):
        # Get total possible score
        # Get amount of challenges
        # Divide score by challenges to get brackets
        # Get standings
        # Iterate over standings and increment the count for each bracket for each standing within that bracket
        return {"success": True, "data": data}