    
from CTFd.cache import clear_challenges, clear_standings
from CTFd.schemas.users import UserSchema
from CTFd.utils.security.auth import update_user
from CTFd.utils.user import get_current_user
from flask import abort, request, session
from flask_restx import Namespace, Resource
from CTFd.utils.decorators import authed_only
from CTFd.models import db
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

    # email notifications update
    checked = True if data["notifications"] == 'true' else False
    db.session.query(UserNotifs).filter(UserNotifs.user == user.id).update({'data':checked})
    db.session.commit()

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