from typing import List

from flask import abort, request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.cache import clear_challenges, clear_standings, clear_user_session
from CTFd.constants import RawEnum
from CTFd.models import (
    Awards,
    Notifications,
    Solves,
    Submissions,
    Tracking,
    Unlocks,
    Users,
    db,
)
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.users import UserSchema
from CTFd.utils.config import get_mail_provider
from CTFd.utils.decorators import admins_only, authed_only, ratelimit
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.email import sendmail, user_created_notification
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.security.auth import update_user
from CTFd.utils.user import get_current_user, get_current_user_type, is_admin

users_namespace = Namespace("users", description="Endpoint to retrieve Users")


UserModel = sqlalchemy_to_pydantic(Users)
TransientUserModel = sqlalchemy_to_pydantic(Users, exclude=["id"])


class UserDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: UserModel


class UserListSuccessResponse(PaginatedAPIListSuccessResponse):
    data: List[UserModel]


users_namespace.schema_model(
    "UserDetailedSuccessResponse", UserDetailedSuccessResponse.apidoc()
)

users_namespace.schema_model(
    "UserListSuccessResponse", UserListSuccessResponse.apidoc()
)


@users_namespace.route("")
class UserList(Resource):
    @check_account_visibility
    @users_namespace.doc(
        description="Endpoint to get User objects in bulk",
        responses={
            200: ("Success", "UserListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "affiliation": (str, None),
            "country": (str, None),
            "bracket": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "UserFields",
                    {
                        "name": "name",
                        "website": "website",
                        "country": "country",
                        "bracket": "bracket",
                        "affiliation": "affiliation",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Users, query=q, field=field)

        if is_admin() and request.args.get("view") == "admin":
            users = (
                Users.query.filter_by(**query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100)
            )
        else:
            users = (
                Users.query.filter_by(banned=False, hidden=False, **query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100)
            )

        response = UserSchema(view="user", many=True).dump(users.items)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "meta": {
                "pagination": {
                    "page": users.page,
                    "next": users.next_num,
                    "prev": users.prev_num,
                    "pages": users.pages,
                    "per_page": users.per_page,
                    "total": users.total,
                }
            },
            "success": True,
            "data": response.data,
        }

    @admins_only
    @users_namespace.doc(
        description="Endpoint to create a User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
        params={
            "notify": "Whether to send the created user an email with their credentials"
        },
    )
    def post(self):
        req = request.get_json()
        schema = UserSchema("admin")
        response = schema.load(req)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        if request.args.get("notify"):
            name = response.data.name
            email = response.data.email
            password = req.get("password")

            user_created_notification(addr=email, name=name, password=password)

        clear_standings()
        clear_challenges()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}


@users_namespace.route("/<int:user_id>")
@users_namespace.param("user_id", "User ID")
class UserPublic(Resource):
    @check_account_visibility
    @users_namespace.doc(
        description="Endpoint to get a specific User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)

        user_type = get_current_user_type(fallback="user")
        response = UserSchema(view=user_type).dump(user)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["place"] = user.place
        response.data["score"] = user.score

        return {"success": True, "data": response.data}

    @admins_only
    @users_namespace.doc(
        description="Endpoint to edit a specific User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()
        data = request.get_json()
        data["id"] = user_id

        # Admins should not be able to ban themselves
        if data["id"] == session["id"] and (
            data.get("banned") is True or data.get("banned") == "true"
        ):
            return (
                {"success": False, "errors": {"id": "You cannot ban yourself"}},
                400,
            )

        schema = UserSchema(view="admin", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        # This generates the response first before actually changing the type
        # This avoids an error during User type changes where we change
        # the polymorphic identity resulting in an ObjectDeletedError
        # https://github.com/CTFd/CTFd/issues/1794
        response = schema.dump(response.data)
        db.session.commit()
        db.session.close()

        clear_user_session(user_id=user_id)
        clear_standings()
        clear_challenges()

        return {"success": True, "data": response.data}

    @admins_only
    @users_namespace.doc(
        description="Endpoint to delete a specific User object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, user_id):
        # Admins should not be able to delete themselves
        if user_id == session["id"]:
            return (
                {"success": False, "errors": {"id": "You cannot delete yourself"}},
                400,
            )

        Notifications.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Unlocks.query.filter_by(user_id=user_id).delete()
        Submissions.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
        db.session.close()

        clear_user_session(user_id=user_id)
        clear_standings()
        clear_challenges()

        return {"success": True}


@users_namespace.route("/me")
class UserPrivate(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to get the User object for the current user",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        user = get_current_user()
        response = UserSchema("self").dump(user).data
        response["place"] = user.place
        response["score"] = user.score
        return {"success": True, "data": response}

    @authed_only
    @users_namespace.doc(
        description="Endpoint to edit the User object for the current user",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self):
        user = get_current_user()
        data = request.get_json()
        schema = UserSchema(view="self", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        # Update user's session for the new session hash
        update_user(user)

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()
        clear_challenges()

        return {"success": True, "data": response.data}


@users_namespace.route("/me/solves")
class UserPrivateSolves(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        solves = user.get_solves(admin=True)

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/me/fails")
class UserPrivateFails(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        fails = user.get_fails(admin=True)

        view = "user" if not is_admin() else "admin"

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            response = SubmissionSchema(view=view, many=True).dump(fails)
            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []

        count = len(fails)
        return {"success": True, "data": data, "meta": {"count": count}}


@users_namespace.route("/me/awards")
@users_namespace.param("user_id", "User ID")
class UserPrivateAwards(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        awards = user.get_awards(admin=True)

        view = "user" if not is_admin() else "admin"
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/<user_id>/solves")
@users_namespace.param("user_id", "User ID")
class UserPublicSolves(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)

        solves = user.get_solves(admin=is_admin())

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/<user_id>/fails")
@users_namespace.param("user_id", "User ID")
class UserPublicFails(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)
        fails = user.get_fails(admin=is_admin())

        view = "user" if not is_admin() else "admin"

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            response = SubmissionSchema(view=view, many=True).dump(fails)
            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []

        count = len(fails)
        return {"success": True, "data": data, "meta": {"count": count}}


@users_namespace.route("/<user_id>/awards")
@users_namespace.param("user_id", "User ID or 'me'")
class UserPublicAwards(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)
        awards = user.get_awards(admin=is_admin())

        view = "user" if not is_admin() else "admin"
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/<int:user_id>/email")
@users_namespace.param("user_id", "User ID")
class UserEmails(Resource):
    @admins_only
    @users_namespace.doc(
        description="Endpoint to email a User object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    @ratelimit(method="POST", limit=10, interval=60)
    def post(self, user_id):
        req = request.get_json()
        text = req.get("text", "").strip()
        user = Users.query.filter_by(id=user_id).first_or_404()

        if get_mail_provider() is None:
            return (
                {"success": False, "errors": {"": ["Email settings not configured"]}},
                400,
            )

        if not text:
            return (
                {"success": False, "errors": {"text": ["Email text cannot be empty"]}},
                400,
            )

        result, response = sendmail(addr=user.email, text=text)

        if result is True:
            return {"success": True}
        else:
            return (
                {"success": False, "errors": {"": [response]}},
                400,
            )
