from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.constants import RawEnum
from CTFd.models import Challenges, ModuleAudienceAccess, Modules, db
from CTFd.schemas.modules import (
    ModuleAudienceAccessSchema,
    ModuleChallengeSchema,
    ModuleSchema,
)
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

modules_namespace = Namespace("modules", description="Endpoint to retrieve Modules")


@modules_namespace.route("")
class ModuleList(Resource):
    @admins_only
    @validate_args(
        {
            "name": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "ModuleFields",
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
        filters = build_model_filters(model=Modules, query=q, field=field)

        modules = (
            Modules.query.filter_by(**query_args)
            .filter(*filters)
            .order_by(Modules.id.asc())
            .all()
        )
        schema = ModuleSchema(many=True)
        response = schema.dump(modules)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = ModuleSchema()
        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()
        response = schema.dump(response.data)
        db.session.close()
        return {"success": True, "data": response.data}


@modules_namespace.route("/<int:module_id>")
class Module(Resource):
    @admins_only
    def get(self, module_id):
        module = Modules.query.filter_by(id=module_id).first_or_404()
        schema = ModuleSchema()
        response = schema.dump(module)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def patch(self, module_id):
        module = Modules.query.filter_by(id=module_id).first_or_404()
        schema = ModuleSchema()
        req = request.get_json()
        response = schema.load(req, session=db.session, instance=module)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()
        response = schema.dump(response.data)
        db.session.close()
        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, module_id):
        module = Modules.query.filter_by(id=module_id).first_or_404()
        db.session.delete(module)
        db.session.commit()
        db.session.close()
        return {"success": True}


@modules_namespace.route("/<int:module_id>/challenges")
class ModuleChallengeList(Resource):
    @admins_only
    def get(self, module_id):
        Modules.query.filter_by(id=module_id).first_or_404()
        challenges = Challenges.query.filter_by(module_id=module_id).all()
        schema = ModuleChallengeSchema(many=True)
        response = schema.dump(challenges)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self, module_id):
        Modules.query.filter_by(id=module_id).first_or_404()
        req = request.get_json() or {}
        challenge_id = req.get("challenge_id")
        if not challenge_id:
            return {
                "success": False,
                "errors": {"challenge_id": ["challenge_id is required"]},
            }, 400

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        challenge.module_id = module_id
        db.session.commit()

        schema = ModuleChallengeSchema()
        response = schema.dump(challenge)
        db.session.close()
        return {"success": True, "data": response.data}


@modules_namespace.route("/<int:module_id>/audiences")
class ModuleAudienceAccessList(Resource):
    @admins_only
    def get(self, module_id):
        Modules.query.filter_by(id=module_id).first_or_404()
        links = ModuleAudienceAccess.query.filter_by(module_id=module_id).all()
        schema = ModuleAudienceAccessSchema(many=True)
        response = schema.dump(links)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self, module_id):
        Modules.query.filter_by(id=module_id).first_or_404()
        req = request.get_json() or {}
        req["module_id"] = module_id
        if not req.get("audience_id"):
            return {
                "success": False,
                "errors": {"audience_id": ["audience_id is required"]},
            }, 400

        schema = ModuleAudienceAccessSchema()
        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()
        response = schema.dump(response.data)
        db.session.close()
        return {"success": True, "data": response.data}


@modules_namespace.route("/<int:module_id>/audiences/<int:audience_id>")
class ModuleAudienceAccessItem(Resource):
    @admins_only
    def delete(self, module_id, audience_id):
        link = ModuleAudienceAccess.query.filter_by(
            module_id=module_id, audience_id=audience_id
        ).first_or_404()
        db.session.delete(link)
        db.session.commit()
        db.session.close()
        return {"success": True}
