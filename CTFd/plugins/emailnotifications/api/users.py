    
from CTFd.cache import clear_challenges, clear_standings, clear_user_session
from CTFd.schemas.users import UserSchema
from CTFd.utils.security.auth import update_user
from CTFd.utils.user import get_current_user
from flask import abort, request, session
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.models import Awards, Notifications, Solves, Submissions, Tracking, Unlocks, Users, db
from CTFd.plugins.emailnotifications import notifications_namespace
from CTFd.plugins.emailnotifications import UserNotifs
from CTFd.utils.logging import log


@authed_only
@notifications_namespace.doc(
    description="Endpoint to edit the User object for the current user",
    responses={
        200: ("Success", "UserDetailedSuccessResponse"),
        400: (
            "An error occured processing the provided or stored data",
            "APISimpleErrorResponse",
        ),
    },
)
def updateUser(request):
    user = get_current_user()
    data = request.get_json()

    # update rest of user data
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

@admins_only
@notifications_namespace.doc(
    description="Endpoint to edit a specific User object",
    responses={
        200: ("Success", "UserDetailedSuccessResponse"),
        400: (
            "An error occured processing the provided or stored data",
            "APISimpleErrorResponse",
        ),
    },
)
def patchUser(request, user_id):
    user = Users.query.filter_by(id=user_id).first_or_404()
    data = request.get_json()
    data["id"] = user.id if user else user_id

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
@notifications_namespace.doc(
    description="Endpoint to delete a specific User object",
    responses={200: ("Success", "APISimpleSuccessResponse")},
)
def deleteUser(user_id):
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
