from flask import Blueprint, current_app
from flask_restx import Api
from CTFd.api.v1.challenges import challenges_namespace
from CTFd.api.v1.flags import flags_namespace
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    APISimpleErrorResponse,
    APISimpleSuccessResponse,
)
api = Blueprint("userChallengeApi", __name__, url_prefix="/apiModding")
User_API_v1 = Api(
    api,
    version="v1",
    doc=current_app.config.get("SWAGGER_UI_ENDPOINT"),
    authorizations={
        "AccessToken": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Generate access token in the settings page of your user account.",
        },
    },
    security=["AccessToken"],
)

User_API_v1.schema_model("APISimpleErrorResponse", APISimpleErrorResponse.schema())
User_API_v1.schema_model(
    "APIDetailedSuccessResponse", APIDetailedSuccessResponse.schema()
)
User_API_v1.schema_model("APISimpleSuccessResponse", APISimpleSuccessResponse.schema())

User_API_v1.add_namespace(challenges_namespace, "/challenges")
User_API_v1.add_namespace(flags_namespace, "/flags")
