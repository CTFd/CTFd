from flask_restx import Resource
from sqlalchemy import func

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Submissions
from CTFd.utils.decorators import admins_only


@statistics_namespace.route("/submissions/<column>")
class SubmissionPropertyCounts(Resource):
    @admins_only
    def get(self, column):
        if column in Submissions.__table__.columns.keys():
            prop = getattr(Submissions, column)
            data = (
                Submissions.query.with_entities(prop, func.count(prop))
                .group_by(prop)
                .all()
            )
            return {"success": True, "data": dict(data)}
        else:
            response = {"success": False, "errors": "That could not be found"}, 404
            return response
