from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_standings
from CTFd.models import Submissions, db
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.utils.decorators import admins_only

submissions_namespace = Namespace(
    "submissions", description="Endpoint to retrieve Submission"
)

SubmissionModel = sqlalchemy_to_pydantic(Submissions)
TransientSubmissionModel = sqlalchemy_to_pydantic(Submissions, exclude=["id"])


class SubmissionDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: SubmissionModel


class SubmissionListSuccessResponse(APIListSuccessResponse):
    data: List[SubmissionModel]


submissions_namespace.schema_model(
    "SubmissionDetailedSuccessResponse", SubmissionDetailedSuccessResponse.apidoc()
)

submissions_namespace.schema_model(
    "SubmissionListSuccessResponse", SubmissionListSuccessResponse.apidoc()
)


@submissions_namespace.route("")
class SubmissionsList(Resource):
    @admins_only
    @submissions_namespace.doc(
        description="Endpoint to get submission objects in bulk",
        responses={
            200: ("Success", "SubmissionListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
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
    @submissions_namespace.doc(
        description="Endpoint to create a submission object. Users should interact with the attempt endpoint to submit flags.",
        responses={
            200: ("Success", "SubmissionListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(TransientSubmissionModel, location="json")
    def post(self, json_args):
        req = json_args
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
    @submissions_namespace.doc(
        description="Endpoint to get submission objects in bulk",
        responses={
            200: ("Success", "SubmissionDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        schema = SubmissionSchema()
        response = schema.dump(submission)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @submissions_namespace.doc(
        description="Endpoint to get submission objects in bulk",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def delete(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        db.session.delete(submission)
        db.session.commit()
        db.session.close()

        # Delete standings cache
        clear_standings()

        return {"success": True}
