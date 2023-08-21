from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Hints, HintUnlocks, db
from CTFd.schemas.hints import HintSchema
from CTFd.utils.decorators import admins_only, during_ctf_time_only
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import get_current_user, is_admin

hints_namespace = Namespace("hints", description="Endpoint to retrieve Hints")

HintModel = sqlalchemy_to_pydantic(Hints)


class HintDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: HintModel


class HintListSuccessResponse(APIListSuccessResponse):
    data: List[HintModel]


hints_namespace.schema_model(
    "HintDetailedSuccessResponse", HintDetailedSuccessResponse.apidoc()
)

hints_namespace.schema_model(
    "HintListSuccessResponse", HintListSuccessResponse.apidoc()
)


@hints_namespace.route("")
class HintList(Resource):
    @admins_only
    @hints_namespace.doc(
        description="Endpoint to list Hint objects in bulk",
        responses={
            200: ("Success", "HintListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "type": (str, None),
            "challenge_id": (int, None),
            "content": (str, None),
            "cost": (int, None),
            "q": (str, None),
            "field": (
                RawEnum("HintFields", {"type": "type", "content": "content"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Hints, query=q, field=field)

        hints = Hints.query.filter_by(**query_args).filter(*filters).all()
        response = HintSchema(many=True, view="locked").dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @hints_namespace.doc(
        description="Endpoint to create a Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = HintSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}


@hints_namespace.route("/<hint_id>")
class Hint(Resource):
    @during_ctf_time_only
    @check_challenge_visibility
    @hints_namespace.doc(
        description="Endpoint to get a specific Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        user = get_current_user()

        # We allow public accessing of hints if challenges are visible and there is no cost or prerequisites
        # If there is a cost or a prereq we should block the user from seeing the hint
        if user is None:
            if hint.cost or hint.prerequisites:
                return (
                    {
                        "success": False,
                        "errors": {"cost": ["You must login to unlock this hint"]},
                    },
                    403,
                )

        if hint.prerequisites:
            requirements = hint.prerequisites

            # Get the IDs of all hints that the user has unlocked
            all_unlocks = HintUnlocks.query.filter_by(account_id=user.account_id).all()
            unlock_ids = {unlock.target for unlock in all_unlocks}

            # Get the IDs of all free hints
            free_hints = Hints.query.filter_by(cost=0).all()
            free_ids = {h.id for h in free_hints}

            # Add free hints to unlocked IDs
            unlock_ids.update(free_ids)

            # Filter out hint IDs that don't exist
            all_hint_ids = {h.id for h in Hints.query.with_entities(Hints.id).all()}
            prereqs = set(requirements).intersection(all_hint_ids)

            # If the user has the necessary unlocks or is admin we should allow them to view
            if unlock_ids >= prereqs or is_admin():
                pass
            else:
                return (
                    {
                        "success": False,
                        "errors": {
                            "requirements": [
                                "You must unlock other hints before accessing this hint"
                            ]
                        },
                    },
                    403,
                )

        view = "unlocked"
        if hint.cost:
            view = "locked"
            unlocked = HintUnlocks.query.filter_by(
                account_id=user.account_id, target=hint.id
            ).first()
            if unlocked:
                view = "unlocked"

        if is_admin():
            if request.args.get("preview", False):
                view = "admin"

        response = HintSchema(view=view).dump(hint)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @hints_namespace.doc(
        description="Endpoint to edit a specific Hint object",
        responses={
            200: ("Success", "HintDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        req = request.get_json()

        schema = HintSchema(view="admin")
        response = schema.load(req, instance=hint, partial=True, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}

    @admins_only
    @hints_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        db.session.delete(hint)
        db.session.commit()
        db.session.close()

        return {"success": True}
