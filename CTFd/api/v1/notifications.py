from typing import List

from flask import current_app, request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.models import build_model_filters
from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Notifications, db
from CTFd.schemas.notifications import NotificationSchema
from CTFd.utils.decorators import admins_only

notifications_namespace = Namespace(
    "notifications", description="Endpoint to retrieve Notifications"
)

NotificationModel = sqlalchemy_to_pydantic(Notifications)
TransientNotificationModel = sqlalchemy_to_pydantic(Notifications, exclude=["id"])


class NotificationDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: NotificationModel


class NotificationListSuccessResponse(APIListSuccessResponse):
    data: List[NotificationModel]


notifications_namespace.schema_model(
    "NotificationDetailedSuccessResponse", NotificationDetailedSuccessResponse.apidoc()
)

notifications_namespace.schema_model(
    "NotificationListSuccessResponse", NotificationListSuccessResponse.apidoc()
)


@notifications_namespace.route("")
class NotificantionList(Resource):
    @notifications_namespace.doc(
        description="Endpoint to get notification objects in bulk",
        responses={
            200: ("Success", "NotificationListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "title": (str, None),
            "content": (str, None),
            "user_id": (int, None),
            "team_id": (int, None),
            "q": (str, None),
            "field": (
                RawEnum("NotificationFields", {"title": "title", "content": "content"}),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Notifications, query=q, field=field)

        notifications = (
            Notifications.query.filter_by(**query_args).filter(*filters).all()
        )
        schema = NotificationSchema(many=True)
        result = schema.dump(notifications)
        if result.errors:
            return {"success": False, "errors": result.errors}, 400
        return {"success": True, "data": result.data}

    @admins_only
    @notifications_namespace.doc(
        description="Endpoint to create a notification object",
        responses={
            200: ("Success", "NotificationDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()

        schema = NotificationSchema()
        result = schema.load(req)

        if result.errors:
            return {"success": False, "errors": result.errors}, 400

        db.session.add(result.data)
        db.session.commit()

        response = schema.dump(result.data)

        # Grab additional settings
        notif_type = req.get("type", "alert")
        notif_sound = req.get("sound", True)
        response.data["type"] = notif_type
        response.data["sound"] = notif_sound

        current_app.events_manager.publish(data=response.data, type="notification")

        return {"success": True, "data": response.data}


@notifications_namespace.route("/<notification_id>")
@notifications_namespace.param("notification_id", "A Notification ID")
class Notification(Resource):
    @notifications_namespace.doc(
        description="Endpoint to get a specific notification object",
        responses={
            200: ("Success", "NotificationDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, notification_id):
        notif = Notifications.query.filter_by(id=notification_id).first_or_404()
        schema = NotificationSchema()
        response = schema.dump(notif)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @notifications_namespace.doc(
        description="Endpoint to delete a notification object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, notification_id):
        notif = Notifications.query.filter_by(id=notification_id).first_or_404()
        db.session.delete(notif)
        db.session.commit()
        db.session.close()

        return {"success": True}
