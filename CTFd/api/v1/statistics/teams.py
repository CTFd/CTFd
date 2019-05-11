from flask_restplus import Resource
from CTFd.models import Teams
from CTFd.utils.decorators import admins_only
from CTFd.api.v1.statistics import statistics_namespace


@statistics_namespace.route("/teams")
class TeamStatistics(Resource):
    @admins_only
    def get(self):
        registered = Teams.query.count()
        data = {"registered": registered}
        return {"success": True, "data": data}
