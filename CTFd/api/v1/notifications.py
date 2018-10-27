from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Notifications
from CTFd.schemas.notifications import NotificationSchema
from CTFd.utils.events import socketio

from CTFd.utils.decorators import (
    admins_only
)

notifications_namespace = Namespace('notifications', description="Endpoint to retrieve Notifications")


@notifications_namespace.route('')
class NotificantionList(Resource):
    def get(self):
        notifications = Notifications.query.all()
        schema = NotificationSchema(many=True)
        result = schema.dump(notifications)
        if result.errors:
            return {
                'success': False,
                'errors': result.errors
            }, 400
        return {
            'success': True,
            'data': result.data
        }

    @admins_only
    def post(self):
        req = request.get_json()

        schema = NotificationSchema()
        result = schema.load(req)

        if result.errors:
            return {
                'success': False,
                'errors': result.errors
            }, 400

        db.session.add(result.data)
        db.session.commit()

        response = schema.dump(result.data)
        socketio.emit('notification', response.data, broadcast=True)

        return {
            'success': True,
            'data': response.data
        }
