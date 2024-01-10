from flask import abort, request
from flask_restx import Namespace, Resource

from CTFd.models import Brackets
from CTFd.schemas.brackets import BracketSchema
from CTFd.utils import get_config
from CTFd.utils.decorators import authed_only
from CTFd.utils.social import get_social_share
from CTFd.utils.user import get_current_user_attrs

brackets_namespace = Namespace("brackets", description="Endpoint to retrieve Brackets")


@brackets_namespace.route("")
class Bracket(Resource):
    def get(self):
        brackets = Brackets.query.all()
        schema = BracketSchema(many=True)
        response = schema.dump(brackets)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}
