from flask import request
from flask_restx import Namespace, Resource

from webargs import fields
from webargs.flaskparser import use_args

from CTFd.cache import clear_standings
from CTFd.models import Submissions, db
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.api import build_endpoint_docs

submissions_namespace = Namespace(
    "submissions", description="Endpoint to retrieve Submission"
)


@submissions_namespace.route("")
class SubmissionsList(Resource):
    args = {
        "ids": fields.DelimitedList(
            fields.Int(), doc="Comma seperated list of Submission IDs"
        ),
        "challenge_id": fields.Int(doc="The challenge ID associated with submissions"),
        "user_id": fields.Int(doc="The user ID associated with submissions"),
        "team_id": fields.Int(doc="The team ID associated with submissions"),
        "ip": fields.Str(doc="The IP address associated with submissions"),
        "provided": fields.Str(doc="The submitted value"),
        "type": fields.Str(doc="The type of submission (e.g. correct, incorrect)"),
    }

    @admins_only
    @use_args(args)
    @submissions_namespace.doc(params=build_endpoint_docs(args))
    def get(self, args):
        schema = SubmissionSchema(many=True)
        ids = args.get("ids")
        if ids:
            query = Submissions.query.filter(Submissions.id.in_(ids)).paginate()
            submissions = query.items
        else:
            query = Submissions.query.filter_by(**args).paginate()
            submissions = query.items

        response = schema.dump(submissions)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "success": True,
            "data": response.data,
            "page": query.page,
            "pages": query.pages,
            "total": query.total,
        }

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

    @admins_only
    @use_args(args)
    @submissions_namespace.doc(params=build_endpoint_docs({"ids": args["ids"]}))
    def delete(self, args):
        ids = args.get("ids", [])
        Submissions.query.filter(Submissions.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()
        db.session.close()

        clear_standings()

        return {"success": True}


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
