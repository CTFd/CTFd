from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Awards
from CTFd.schemas.awards import AwardSchema
from CTFd.utils.events import socketio

from CTFd.utils.decorators import (
    admins_only
)

announcements_namespace = Namespace('announcements', description="Endpoint to retrieve Announcements")


@announcements_namespace.route('')
class AnnouncementList(Resource):
    @admins_only
    def get(self):
        pass

    @admins_only
    def post(self):
        req = request.get_json()
        socketio.emit('announcement', req, broadcast=True)
        return req
