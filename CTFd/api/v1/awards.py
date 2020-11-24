from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_standings
from CTFd.constants import RawEnum
from CTFd.models import Awards, Users, db
from CTFd.schemas.awards import AwardSchema
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

awards_namespace = Namespace("awards", description="Endpoint to retrieve Awards")

AwardModel = sqlalchemy_to_pydantic(Awards)


class AwardDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: AwardModel


class AwardListSuccessResponse(APIListSuccessResponse):
    data: List[AwardModel]


awards_namespace.schema_model(
    "AwardDetailedSuccessResponse", AwardDetailedSuccessResponse.apidoc()
)

awards_namespace.schema_model(
    "AwardListSuccessResponse", AwardListSuccessResponse.apidoc()
)


@awards_namespace.route("")
class AwardList(Resource):
    @admins_only
    @awards_namespace.doc(
        description="Endpoint to list Award objects in bulk",
        responses={
            200: ("Success", "AwardListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "user_id": (int, None),
            "team_id": (int, None),
            "type": (str, None),
            "value": (int, None),
            "category": (int, None),
            "icon": (int, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "AwardFields",
                    {
                        "name": "name",
                        "description": "description",
                        "category": "category",
                        "icon": "icon",
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
        filters = build_model_filters(model=Awards, query=q, field=field)

        awards = Awards.query.filter_by(**query_args).filter(*filters).all()
        schema = AwardSchema(many=True)
        response = schema.dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @awards_namespace.doc(
        description="Endpoint to create an Award object",
        responses={
            200: ("Success", "AwardListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()

        # Force a team_id if in team mode and unspecified
        if is_teams_mode():
            team_id = req.get("team_id")
            if team_id is None:
                user = Users.query.filter_by(id=req["user_id"]).first_or_404()
                if user.team_id is None:
                    return (
                        {
                            "success": False,
                            "errors": {
                                "team_id": [
                                    "User doesn't have a team to associate award with"
                                ]
                            },
                        },
                        400,
                    )
                req["team_id"] = user.team_id

        schema = AwardSchema()

        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        # Delete standings cache because awards can change scores
        clear_standings()

        return {"success": True, "data": response.data}


@awards_namespace.route("/<award_id>")
@awards_namespace.param("award_id", "An Award ID")
class Award(Resource):
    @admins_only
    @awards_namespace.doc(
        description="Endpoint to get a specific Award object",
        responses={
            200: ("Success", "AwardDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        response = AwardSchema().dump(award)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @awards_namespace.doc(
        description="Endpoint to delete an Award object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        db.session.delete(award)
        db.session.commit()
        db.session.close()

        # Delete standings cache because awards can change scores
        clear_standings()

        return {"success": True}
