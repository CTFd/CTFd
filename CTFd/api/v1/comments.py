from typing import List

from flask import request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.models import build_model_filters
from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import (
    ChallengeComments,
    Comments,
    PageComments,
    TeamComments,
    UserComments,
    db,
)
from CTFd.schemas.comments import CommentSchema
from CTFd.utils.decorators import admins_only

comments_namespace = Namespace("comments", description="Endpoint to retrieve Comments")


@comments_namespace.route("")
class CommentList(Resource):
    # @admins_only
    # def get(self, query_args):
    #     q = query_args.pop("q", None)
    #     field = str(query_args.pop("field", None))
    #     filters = build_model_filters(model=Tags, query=q, field=field)

    #     tags = Tags.query.filter_by(**query_args).filter(*filters).all()
    #     schema = TagSchema(many=True)
    #     response = schema.dump(tags)

    #     if response.errors:
    #         return {"success": False, "errors": response.errors}, 400

    #     return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()

        req["author_id"] = session["id"]

        model = Comments
        if "challenge_id" in req:
            model = ChallengeComments
        elif "user_id" in req:
            model = ChallengeComments
        elif "team_id" in req:
            model = TeamComments
        elif "page_id" in req:
            model = PageComments
        else:
            model = Comments

        m = model(**req)
        db.session.add(m)
        db.session.commit()

        schema = CommentSchema()

        response = schema.dump(m)
        db.session.close()

        return {"success": True, "data": response.data}
