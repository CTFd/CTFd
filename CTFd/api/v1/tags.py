from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Tags
from CTFd.schemas.tags import TagSchema
from CTFd.utils.decorators import admins_only

tags_namespace = Namespace("tags", description="Endpoint to retrieve Tags")


@tags_namespace.route("")
class TagList(Resource):
    @admins_only
    def get(self):
        # TODO: Filter by challenge_id
        tags = Tags.query.all()
        schema = TagSchema(many=True)
        response = schema.dump(tags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = TagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@tags_namespace.route("/<tag_id>")
@tags_namespace.param("tag_id", "A Tag ID")
class Tag(Resource):
    @admins_only
    def get(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()

        response = TagSchema().dump(tag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def patch(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}
