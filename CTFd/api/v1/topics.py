from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Topics, db
from CTFd.schemas.topics import TopicSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

topics_namespace = Namespace("topics", description="Endpoint to retrieve Topics")


@topics_namespace.route("")
class TopicList(Resource):
    @admins_only
    @validate_args(
        {
            "value": (str, None),
            "q": (str, None),
            "field": (RawEnum("TopicFields", {"value": "value"}), None,),
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
    def post(self):
        req = request.get_json()
        schema = TopicSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@topics_namespace.route("/<topic_id>")
class Topic(Resource):
    @admins_only
    def get(self, topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        response = TopicSchema().dump(topic)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
