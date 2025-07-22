from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Solutions, db
from CTFd.schemas.solutions import SolutionSchema
from CTFd.utils import user as current_user
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.helpers.models import build_model_filters

solutions_namespace = Namespace(
    "solutions", description="Endpoint to retrieve and create Solutions"
)

SolutionModel = sqlalchemy_to_pydantic(Solutions)
TransientSolutionModel = sqlalchemy_to_pydantic(Solutions, exclude=["id"])


class SolutionDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: SolutionModel


class SolutionListSuccessResponse(APIListSuccessResponse):
    data: List[SolutionModel]


solutions_namespace.schema_model(
    "SolutionDetailedSuccessResponse", SolutionDetailedSuccessResponse.apidoc()
)

solutions_namespace.schema_model(
    "SolutionListSuccessResponse", SolutionListSuccessResponse.apidoc()
)


@solutions_namespace.route("")
class SolutionsList(Resource):
    @admins_only
    @solutions_namespace.doc(
        description="Endpoint to get solution objects in bulk",
        responses={
            200: ("Success", "SolutionListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "state": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "SolutionFields",
                    {
                        "challenge_id": "challenge_id",
                        "state": "state",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Solutions, query=q, field=field)

        args = query_args
        schema = SolutionSchema(many=True)

        solutions = Solutions.query.filter_by(**args).filter(*filters).all()

        response = schema.dump(solutions)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "success": True,
            "data": response.data,
        }

    @admins_only
    @solutions_namespace.doc(
        description="Endpoint to create a solution object",
        responses={
            200: ("Success", "SolutionDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
            403: (
                "Access denied",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, True),
            "state": (str, False),
        },
        location="json",
    )
    def post(self, json_args):
        req = json_args

        # Set default state if not provided
        if "state" not in req or req["state"] is None:
            req["state"] = "draft"

        solution = Solutions(**req)
        schema = SolutionSchema()

        try:
            db.session.add(solution)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"success": False, "errors": str(e)}, 400

        response = schema.dump(solution)
        db.session.close()

        return {"success": True, "data": response.data}


@solutions_namespace.route("/<solution_id>")
@solutions_namespace.param("solution_id", "A Solution ID")
class Solution(Resource):
    @authed_only
    @solutions_namespace.doc(
        description="Endpoint to get a solution object",
        responses={
            200: ("Success", "SolutionDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, solution_id):
        solution = Solutions.query.filter_by(id=solution_id).first_or_404()
        schema = SolutionSchema()
        response = schema.dump(solution)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @solutions_namespace.doc(
        description="Endpoint to edit a solution object",
        responses={
            200: ("Success", "SolutionDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, False),
            "content": (str, False),
            "state": (str, False),
        },
        location="json",
    )
    def patch(self, solution_id, json_args):
        solution = Solutions.query.filter_by(id=solution_id).first_or_404()

        req = json_args
        schema = SolutionSchema()

        try:
            for key, value in req.items():
                if hasattr(solution, key):
                    setattr(solution, key, value)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"success": False, "errors": str(e)}, 400

        response = schema.dump(solution)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    @solutions_namespace.doc(
        description="Endpoint to delete a solution object",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def delete(self, solution_id):
        solution = Solutions.query.filter_by(id=solution_id).first_or_404()

        try:
            db.session.delete(solution)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"success": False, "errors": str(e)}, 400

        db.session.close()

        return {"success": True}
