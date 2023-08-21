from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import ChallengeTopics, Topics, db
from CTFd.schemas.topics import ChallengeTopicSchema, TopicSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

topics_namespace = Namespace("topics", description="Endpoint to retrieve Topics")

TopicModel = sqlalchemy_to_pydantic(Topics)


class TopicDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TopicModel


class TopicListSuccessResponse(APIListSuccessResponse):
    data: List[TopicModel]


topics_namespace.schema_model(
    "TopicDetailedSuccessResponse", TopicDetailedSuccessResponse.apidoc()
)

topics_namespace.schema_model(
    "TopicListSuccessResponse", TopicListSuccessResponse.apidoc()
)


@topics_namespace.route("")
class TopicList(Resource):
    @admins_only
    @topics_namespace.doc(
        description="Endpoint to list Topic objects in bulk",
        responses={
            200: ("Success", "TopicListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "value": (str, None),
            "q": (str, None),
            "field": (
                RawEnum("TopicFields", {"value": "value"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Topics, query=q, field=field)

        topics = Topics.query.filter_by(**query_args).filter(*filters).all()
        schema = TopicSchema(many=True)
        response = schema.dump(topics)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @topics_namespace.doc(
        description="Endpoint to create a Topic object",
        responses={
            200: ("Success", "TopicDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        value = req.get("value")

        if value:
            topic = Topics.query.filter_by(value=value).first()
            if topic is None:
                schema = TopicSchema()
                response = schema.load(req, session=db.session)

                if response.errors:
                    return {"success": False, "errors": response.errors}, 400

                topic = response.data
                db.session.add(topic)
                db.session.commit()
        else:
            topic_id = req.get("topic_id")
            topic = Topics.query.filter_by(id=topic_id).first_or_404()

        req["topic_id"] = topic.id
        topic_type = req.get("type")
        if topic_type == "challenge":
            schema = ChallengeTopicSchema()
            response = schema.load(req, session=db.session)
        else:
            return {"success": False}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    @topics_namespace.doc(
        description="Endpoint to delete a specific Topic object of a specific type",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    @validate_args(
        {"type": (str, None), "target_id": (int, 0)},
        location="query",
    )
    def delete(self, query_args):
        topic_type = query_args.get("type")
        target_id = int(query_args.get("target_id", 0))

        if topic_type == "challenge":
            Model = ChallengeTopics
        else:
            return {"success": False}, 400

        topic = Model.query.filter_by(id=target_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}


@topics_namespace.route("/<topic_id>")
class Topic(Resource):
    @admins_only
    @topics_namespace.doc(
        description="Endpoint to get a specific Topic object",
        responses={
            200: ("Success", "TopicDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        response = TopicSchema().dump(topic)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @topics_namespace.doc(
        description="Endpoint to delete a specific Topic object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
