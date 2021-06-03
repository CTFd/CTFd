from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Tags, db
from CTFd.schemas.tags import TagSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

tags_namespace = Namespace("tags", description="Endpoint to retrieve Tags")

TagModel = sqlalchemy_to_pydantic(Tags)


class TagDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TagModel


class TagListSuccessResponse(APIListSuccessResponse):
    data: List[TagModel]


tags_namespace.schema_model(
    "TagDetailedSuccessResponse", TagDetailedSuccessResponse.apidoc()
)

tags_namespace.schema_model("TagListSuccessResponse", TagListSuccessResponse.apidoc())


@tags_namespace.route("")
class TagList(Resource):
    @admins_only
    @tags_namespace.doc(
        description="Endpoint to list Tag objects in bulk",
        responses={
            200: ("Success", "TagListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "value": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "TagFields", {"challenge_id": "challenge_id", "value": "value"}
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Tags, query=q, field=field)

        tags = Tags.query.filter_by(**query_args).filter(*filters).all()
        schema = TagSchema(many=True)
        response = schema.dump(tags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @tags_namespace.doc(
        description="Endpoint to create a Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        schema = TagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@tags_namespace.route("/<tag_id>")
@tags_namespace.param("tag_id", "A Tag ID")
class Tag(Resource):
    @admins_only
    @tags_namespace.doc(
        description="Endpoint to get a specific Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()

        response = TagSchema().dump(tag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @tags_namespace.doc(
        description="Endpoint to edit a specific Tag object",
        responses={
            200: ("Success", "TagDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    @tags_namespace.doc(
        description="Endpoint to delete a specific Tag object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}
