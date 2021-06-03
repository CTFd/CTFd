from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Flags, db
from CTFd.plugins.flags import FLAG_CLASSES, get_flag_class
from CTFd.schemas.flags import FlagSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

flags_namespace = Namespace("flags", description="Endpoint to retrieve Flags")

FlagModel = sqlalchemy_to_pydantic(Flags)


class FlagDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: FlagModel


class FlagListSuccessResponse(APIListSuccessResponse):
    data: List[FlagModel]


flags_namespace.schema_model(
    "FlagDetailedSuccessResponse", FlagDetailedSuccessResponse.apidoc()
)

flags_namespace.schema_model(
    "FlagListSuccessResponse", FlagListSuccessResponse.apidoc()
)


@flags_namespace.route("")
class FlagList(Resource):
    @admins_only
    @flags_namespace.doc(
        description="Endpoint to list Flag objects in bulk",
        responses={
            200: ("Success", "FlagListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "type": (str, None),
            "content": (str, None),
            "data": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "FlagFields", {"type": "type", "content": "content", "data": "data"}
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Flags, query=q, field=field)

        flags = Flags.query.filter_by(**query_args).filter(*filters).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @flags_namespace.doc(
        description="Endpoint to create a Flag object",
        responses={
            200: ("Success", "FlagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = FlagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@flags_namespace.route("/types", defaults={"type_name": None})
@flags_namespace.route("/types/<type_name>")
class FlagTypes(Resource):
    @admins_only
    def get(self, type_name):
        if type_name:
            flag_class = get_flag_class(type_name)
            response = {"name": flag_class.name, "templates": flag_class.templates}
            return {"success": True, "data": response}
        else:
            response = {}
            for class_id in FLAG_CLASSES:
                flag_class = FLAG_CLASSES.get(class_id)
                response[class_id] = {
                    "name": flag_class.name,
                    "templates": flag_class.templates,
                }
            return {"success": True, "data": response}


@flags_namespace.route("/<flag_id>")
class Flag(Resource):
    @admins_only
    @flags_namespace.doc(
        description="Endpoint to get a specific Flag object",
        responses={
            200: ("Success", "FlagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        response = schema.dump(flag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["templates"] = get_flag_class(flag.type).templates

        return {"success": True, "data": response.data}

    @admins_only
    @flags_namespace.doc(
        description="Endpoint to delete a specific Flag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()

        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        return {"success": True}

    @admins_only
    @flags_namespace.doc(
        description="Endpoint to edit a specific Flag object",
        responses={
            200: ("Success", "FlagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=flag, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
