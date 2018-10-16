from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Pages
from CTFd.schemas.pages import PageSchema
from CTFd.utils.events import socketio

from CTFd.utils.decorators import (
    admins_only
)

pages_namespace = Namespace('pages', description="Endpoint to retrieve Pages")


@pages_namespace.route('')
class PageList(Resource):
    @admins_only
    def get(self):
        pages = Pages.query.all()
        schema = PageSchema(exclude=['content'], many=True)
        result = schema.dump(pages)
        if result.errors:
            return result.errors
        return result.data

    @admins_only
    def post(self):
        pass


@pages_namespace.route('/<page_id>')
class PageDetail(Resource):
    @admins_only
    def get(self, page_id):
        pass

    @admins_only
    def patch(self, page_id):
        pass

    @admins_only
    def delete(self, page_id):
        pass