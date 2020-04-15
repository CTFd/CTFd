from flask_restx import Resource
from sqlalchemy import func

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Submissions
from CTFd.utils.decorators import admins_only
from CTFd.utils.scores import get_standings


@statistics_namespace.route("/scores/distribution")
class ScoresDistribution(Resource):
    @admins_only
    def get(self):
        challenge_count = Challenges.query.count()
        total_points = (
            Challenges.query.with_entities(db.func.sum(Challenges.value).label("sum"))
            .filter_by(state="visible")
            .first()
            .sum
        )
        # Divide score by challenges to get brackets
        bracket_size = total_points // challenge_count

        # Get standings
        standings = get_standings(admin=True)

        # Iterate over standings and increment the count for each bracket for each standing within that bracket
        return {"success": True, "data": data}
