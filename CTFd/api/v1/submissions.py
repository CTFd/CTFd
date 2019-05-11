from flask import request
from flask_restplus import Namespace, Resource

from CTFd.cache import clear_standings
from CTFd.models import db, Submissions
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.utils.decorators import admins_only

submissions_namespace = Namespace(
    "submissions", description="Endpoint to retrieve Submission"
)


@submissions_namespace.route("")
class SubmissionsList(Resource):
    @admins_only
    def get(self):
        args = request.args.to_dict()
        schema = SubmissionSchema(many=True)
        if args:
            submissions = Submissions.query.filter_by(**args).all()
        else:
            submissions = Submissions.query.all()

        response = schema.dump(submissions)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        Model = Submissions.get_child(type=req.get("type"))
        schema = SubmissionSchema(instance=Model())
        response = schema.load(req)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        # Delete standings cache
        clear_standings()

        return {"success": True, "data": response.data}


@submissions_namespace.route("/<submission_id>")
@submissions_namespace.param("submission_id", "A Submission ID")
class Submission(Resource):
    @admins_only
    def get(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        schema = SubmissionSchema()
        response = schema.dump(submission)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        db.session.delete(submission)
        db.session.commit()
        db.session.close()

        # Delete standings cache
        clear_standings()

        return {"success": True}
