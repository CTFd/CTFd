from collections import defaultdict

from flask_restx import Resource

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import db, Challenges
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
        # Divide score by challenges to get brackets with explicit floor division
        bracket_size = total_points // challenge_count

        # Get standings
        standings = get_standings(admin=True)

        # Iterate over standings and increment the count for each bracket for each standing within that bracket
        bottom, top = 0, bracket_size
        count = 1
        brackets = defaultdict(lambda: 0)
        for t in reversed(standings):
            if ((t.score >= bottom) and (t.score <= top)) or t.score <= 0:
                brackets[top] += 1
            else:
                count += 1
                bottom, top = (bracket_size, (bracket_size * count))
                brackets[top] += 1

        return {"success": True, "data": {"brackets": brackets}}
