from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Tags
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.schemas.tags import TagSchema
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
        # TODO: Filter by challenge_id
        tags = Tags.query.all()
        schema = TagSchema(many=True)
        result = schema.dump(tags)
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        schema = TagSchema(many=True)
        tags = schema.load(req)

        if tags.errors:
            return tags.errors

        for tag in tags.data:
            db.session.add(tag)
        db.session.commit()
        response = schema.dump(tags.data)
        db.session.close()

        return response


@tags_namespace.route('/<tag_id>')
@tags_namespace.param('tag_id', 'A Tag ID')
class Tag(Resource):
    @admins_only
    def get(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        return TagSchema().dump(tag)

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
    def put(self, tag_id):
        # TODO: This should be PATCH probably
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        tag = schema.load(req, session=db.session, instance=tag)
        if tag.errors:
            return tag.errors

        db.session.commit()
        response = schema.dump(tag.data)
        db.session.close()
        return response