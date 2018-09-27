from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Tags
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    admins_only
)
from sqlalchemy.sql import or_

tags_namespace = Namespace('tags', description="Endpoint to retrieve Tags")


@tags_namespace.route('')
class TagList(Resource):

    @admins_only
    def get(self):
        tags = Tags.query.all()
        return [tag.get_dict() for tag in tags]

    @admins_only
    def post(self):
        pass


@tags_namespace.route('/<tag_id>')
@tags_namespace.param('tag_id', 'A Tag ID')
class Tag(Resource):
    @admins_only
    def get(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        return tag.get_dict()

    @admins_only
    def delete(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        response = {
            'success': True
        }
        return response

    @admins_only
    def put(self):
        pass