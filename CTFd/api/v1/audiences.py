from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.constants import RawEnum
from CTFd.models import AudienceMembers, Audiences, db
from CTFd.schemas.audiences import AudienceMemberSchema, AudienceSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

audiences_namespace = Namespace(
    "audiences", description="Endpoint to retrieve Audiences"
)


@audiences_namespace.route("")
class AudienceList(Resource):
    @admins_only
    @validate_args(
        {
            "name": (str, None),
            "type": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "AudienceFields",
                    {"name": "name", "description": "description"},
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Audiences, query=q, field=field)

        audiences = (
            Audiences.query.filter_by(**query_args)
            .filter(*filters)
            .order_by(Audiences.id.asc())
            .all()
        )
        schema = AudienceSchema(many=True)
        response = schema.dump(audiences)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = AudienceSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@audiences_namespace.route("/<int:audience_id>")
class Audience(Resource):
    @admins_only
    def get(self, audience_id):
        audience = Audiences.query.filter_by(id=audience_id).first_or_404()
        schema = AudienceSchema()
        response = schema.dump(audience)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def patch(self, audience_id):
        audience = Audiences.query.filter_by(id=audience_id).first_or_404()
        schema = AudienceSchema()

        req = request.get_json()
        response = schema.load(req, session=db.session, instance=audience)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()
        response = schema.dump(response.data)
        db.session.close()
        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, audience_id):
        audience = Audiences.query.filter_by(id=audience_id).first_or_404()
        db.session.delete(audience)
        db.session.commit()
        db.session.close()
        return {"success": True}


@audiences_namespace.route("/<int:audience_id>/members")
class AudienceMemberList(Resource):
    @admins_only
    def get(self, audience_id):
        Audiences.query.filter_by(id=audience_id).first_or_404()
        members = AudienceMembers.query.filter_by(audience_id=audience_id).all()
        schema = AudienceMemberSchema(many=True)
        response = schema.dump(members)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self, audience_id):
        Audiences.query.filter_by(id=audience_id).first_or_404()
        req = request.get_json() or {}
        req["audience_id"] = audience_id
        if not req.get("user_id") and not req.get("team_id"):
            return {
                "success": False,
                "errors": {"": ["Either user_id or team_id is required"]},
            }, 400

        schema = AudienceMemberSchema()
        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()
        response = schema.dump(response.data)
        db.session.close()
        return {"success": True, "data": response.data}


@audiences_namespace.route("/<int:audience_id>/members/<int:member_id>")
class AudienceMember(Resource):
    @admins_only
    def delete(self, audience_id, member_id):
        member = AudienceMembers.query.filter_by(
            id=member_id, audience_id=audience_id
        ).first_or_404()
        db.session.delete(member)
        db.session.commit()
        db.session.close()
        return {"success": True}
