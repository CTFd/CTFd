from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Announcements
from CTFd.schemas.announcements import AnnouncementSchema
from CTFd.utils.events import socketio

from CTFd.utils.decorators import (
    admins_only
)

announcements_namespace = Namespace('announcements', description="Endpoint to retrieve Announcements")


@announcements_namespace.route('')
class AnnouncementList(Resource):
    # TODO: Front end to surface Announcements
    def get(self):
        announcements = Announcements.query.all()
        schema = AnnouncementSchema(many=True)
        result = schema.dump(announcements)
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
        a = Announcements(
            content=req['message']
        )
        db.session.add(a)
        db.session.commit()
        socketio.emit('announcement', req, broadcast=True)
        return {
            'success': True,
            'data': req
        }
