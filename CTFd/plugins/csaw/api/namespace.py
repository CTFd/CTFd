import json
from typing import List

from flask import request
from flask import current_app as app
from flask_restx import Namespace, Resource
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.models import Users
from CTFd.plugins.csaw.schema import CSAWMembers
from CTFd.plugins.csaw.utils.members import get_members
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user

csaw_namespace = Namespace("csaw", description="Endpoint to retrieve CSAW")

# UserModel = sqlalchemy_to_pydantic(Users)
# TransientUserModel = sqlalchemy_to_pydantic(Users, exclude=["id"])


# class UserDetailedSuccessResponse(APIDetailedSuccessResponse):
#     data: UserModel


# class UserListSuccessResponse(PaginatedAPIListSuccessResponse):
#     data: List[UserModel]


# csaw_namespace.schema_model(
#     "UserDetailedSuccessResponse", UserDetailedSuccessResponse.apidoc()
# )

# csaw_namespace.schema_model("UserListSuccessResponse", UserListSuccessResponse.apidoc())


# Return the user stuff
@csaw_namespace.route("/members")
class Dummy(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        app.logger.info(user)
        members = get_members(user)
        data = members

        return {"success": True, "data": data}

    # @authed_only
    # def patch(self):
    #     user = get_current_user()
    #     data = request.get_json()
    #     schema = CSAWMembers


# Update the user stuff
# @csaw_namespace.route("/me")
# class CSAWPrivate(Resource):
#     @authed_only
#     @csaw_namespace.doc(
#         description="Endpoint to edit the User object for the current user",
#         responses={
#             200: ("Success", "UserDetailedSuccessResponse"),
#             400: (
#                 "An error occurred processing the provided or stored data",
#                 "APISimpleErrorResponse",
#             ),
#         },
#     )
#     def patch(self):
#         user = get_current_user()
#         data = request.get_json()
#         schema = CSAWSchema(view="self", instance=user, partial=True)
#         response = schema.load(data)
#         if response.errors:
#             return {"success": False, "errors": response.errors}, 400

#         db.session.commit()

#         # Update user's session for the new session hash
#         update_user(user)

#         response = schema.dump(response.data)
#         db.session.close()

#         clear_standings()

#         return {"success": True, "data": response.data}
