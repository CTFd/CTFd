from flask import Blueprint, current_app
from flask_restx import Api

from CTFd.api.v1.awards import awards_namespace
from CTFd.api.v1.brackets import brackets_namespace
from CTFd.api.v1.challenges import challenges_namespace
from CTFd.api.v1.comments import comments_namespace
from CTFd.api.v1.config import configs_namespace
from CTFd.api.v1.exports import exports_namespace
from CTFd.api.v1.files import files_namespace
from CTFd.api.v1.flags import flags_namespace
from CTFd.api.v1.hints import hints_namespace
from CTFd.api.v1.notifications import notifications_namespace
from CTFd.api.v1.pages import pages_namespace
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    APISimpleErrorResponse,
    APISimpleSuccessResponse,
)
from CTFd.api.v1.scoreboard import scoreboard_namespace
from CTFd.api.v1.shares import shares_namespace
from CTFd.api.v1.statistics import statistics_namespace
from CTFd.api.v1.submissions import submissions_namespace
from CTFd.api.v1.tags import tags_namespace
from CTFd.api.v1.teams import teams_namespace
from CTFd.api.v1.tokens import tokens_namespace
from CTFd.api.v1.topics import topics_namespace
from CTFd.api.v1.unlocks import unlocks_namespace
from CTFd.api.v1.users import users_namespace

api = Blueprint("userChallengeApi", __name__, url_prefix="/userChallenge/apiModding")
CTFd_API_v1 = Api(
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

CTFd_API_v1.schema_model("APISimpleErrorResponse", APISimpleErrorResponse.schema())
CTFd_API_v1.schema_model(
    "APIDetailedSuccessResponse", APIDetailedSuccessResponse.schema()
)
CTFd_API_v1.schema_model("APISimpleSuccessResponse", APISimpleSuccessResponse.schema())

CTFd_API_v1.add_namespace(challenges_namespace, "/challenges")
CTFd_API_v1.add_namespace(flags_namespace, "/flags")
