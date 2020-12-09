from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_standings
from CTFd.constants import RawEnum
from CTFd.models import Unlocks, db, get_class_by_tablename
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.unlocks import UnlockSchema
from CTFd.utils.decorators import (
    admins_only,
    authed_only,
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import get_current_user

unlocks_namespace = Namespace("unlocks", description="Endpoint to retrieve Unlocks")

UnlockModel = sqlalchemy_to_pydantic(Unlocks)
TransientUnlockModel = sqlalchemy_to_pydantic(Unlocks, exclude=["id"])


class UnlockDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: UnlockModel


class UnlockListSuccessResponse(APIListSuccessResponse):
    data: List[UnlockModel]


unlocks_namespace.schema_model(
    "UnlockDetailedSuccessResponse", UnlockDetailedSuccessResponse.apidoc()
)

unlocks_namespace.schema_model(
    "UnlockListSuccessResponse", UnlockListSuccessResponse.apidoc()
)


@unlocks_namespace.route("")
class UnlockList(Resource):
    @admins_only
    @unlocks_namespace.doc(
        description="Endpoint to get unlock objects in bulk",
        responses={
            200: ("Success", "UnlockListSuccessResponse"),
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
            "target": (int, None),
            "type": (str, None),
            "q": (str, None),
            "field": (
                RawEnum("UnlockFields", {"target": "target", "type": "type"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Unlocks, query=q, field=field)

        unlocks = Unlocks.query.filter_by(**query_args).filter(*filters).all()
        schema = UnlockSchema()
        response = schema.dump(unlocks)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @during_ctf_time_only
    @require_verified_emails
    @authed_only
    @unlocks_namespace.doc(
        description="Endpoint to create an unlock object. Used to unlock hints.",
        responses={
            200: ("Success", "UnlockDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        user = get_current_user()

        req["user_id"] = user.id
        req["team_id"] = user.team_id

        Model = get_class_by_tablename(req["type"])
        target = Model.query.filter_by(id=req["target"]).first_or_404()

        # We should use the team's score if in teams mode
        # user.account gives the appropriate account based on team mode
        if target.cost > user.account.score:
            return (
                {
                    "success": False,
                    "errors": {
                        "score": "You do not have enough points to unlock this hint"
                    },
                },
                400,
            )

        schema = UnlockSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        # Search for an existing unlock that matches the target and type
        # And matches either the requesting user id or the requesting team id
        existing = Unlocks.query.filter(
            Unlocks.target == req["target"],
            Unlocks.type == req["type"],
            Unlocks.account_id == user.account_id,
        ).first()
        if existing:
            return (
                {
                    "success": False,
                    "errors": {"target": "You've already unlocked this this target"},
                },
                400,
            )

        db.session.add(response.data)

        award_schema = AwardSchema()
        award = {
            "user_id": user.id,
            "team_id": user.team_id,
            "name": target.name,
            "description": target.description,
            "value": (-target.cost),
            "category": target.category,
        }

        award = award_schema.load(award)
        db.session.add(award.data)
        db.session.commit()
        clear_standings()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
