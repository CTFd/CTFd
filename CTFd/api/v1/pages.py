from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Pages
from CTFd.schemas.pages import PageSchema
from CTFd.cache import clear_pages

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
        response = schema.dump(pages)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def post(self):
        req = request.get_json()
        schema = PageSchema()
        response = schema.load(req)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_pages()

        return {
            'success': True,
            'data': response.data
        }


@pages_namespace.route('/<page_id>')
class PageDetail(Resource):
    @admins_only
    def get(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        schema = PageSchema()
        response = schema.dump(page)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        req = request.get_json()

        schema = PageSchema(partial=True)
        response = schema.load(req, instance=page, partial=True)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_pages()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        db.session.delete(page)
        db.session.commit()
        db.session.close()

        clear_pages()

        return {
            'success': True
        }
