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
            return result.errors, 400
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        schema = PageSchema()
        page = schema.load(req)
        if page.errors:
            return page.errors, 400

        db.session.add(page.data)
        db.session.commit()
        response = schema.dump(page.data)
        db.session.close()

        return response


@pages_namespace.route('/<page_id>')
class PageDetail(Resource):
    @admins_only
    def get(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        schema = PageSchema()
        result = schema.dump(page)
        if result.errors:
            return result.errors, 400
        return result.data

    @admins_only
    def patch(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        req = request.get_json()

        schema = PageSchema(partial=True)
        page = schema.load(req, instance=page, partial=True)
        if page.errors:
            return page.errors, 400

        db.session.commit()
        response = schema.dump(page.data)
        db.session.close()
        return response

    @admins_only
    def delete(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        db.session.delete(page)
        db.session.commit()
        db.session.close()

        return {
            'success': True
        }
