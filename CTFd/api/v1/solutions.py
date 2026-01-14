from typing import List

from flask import abort, request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Solutions, SolutionUnlocks, db
from CTFd.schemas.solutions import SolutionSchema
from CTFd.utils.challenges import get_solve_ids_for_user_id
from CTFd.utils.decorators import (
    admins_only,
    authed_only,
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import get_current_user, is_admin

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
class SolutionList(Resource):
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
            "state": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "SolutionFields",
                    {
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
        TransientSolutionModel,
        location="json",
    )
    def post(self, json_args):
        req = json_args

        # Set default state if not provided
        if "state" not in req or req["state"] is None:
            req["state"] = "hidden"

        solution = Solutions(**req)
        schema = SolutionSchema()

        db.session.add(solution)
        db.session.commit()

        response = schema.dump(solution)
        db.session.close()

        return {"success": True, "data": response.data}


@solutions_namespace.route("/<solution_id>")
@solutions_namespace.param("solution_id", "A Solution ID")
class Solution(Resource):
    @during_ctf_time_only
    @require_verified_emails
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

        user = get_current_user()

        if is_admin():
            view = "admin"
        else:
            if solution.state == "hidden":
                abort(404)
            if solution.challenge.state == "hidden":
                abort(404)

            # If the solution state is visible we just let it through
            if solution.state == "visible":
                pass
            elif solution.state == "solved":
                user_solves = get_solve_ids_for_user_id(user_id=user.id)
                if solution.challenge.id not in user_solves:
                    abort(404)
            else:
                # Different behavior can be implemented in a plugin for the route
                abort(404)

            view = "locked"
            unlocked = SolutionUnlocks.query.filter_by(
                account_id=user.account_id, target=solution.id
            ).first()
            if unlocked:
                view = "unlocked"

        schema = SolutionSchema(view=view)
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
    def patch(self, solution_id):
        solution = Solutions.query.filter_by(id=solution_id).first_or_404()

        req = request.get_json()
        schema = SolutionSchema(partial=True)

        response = schema.load(req, instance=solution, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

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

        db.session.delete(solution)
        db.session.commit()

        return {"success": True}
