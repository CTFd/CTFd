from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Flags
from CTFd.schemas.flags import FlagSchema
from CTFd.plugins.flags import get_flag_class, FLAG_CLASSES
from CTFd.utils.decorators import admins_only

flags_namespace = Namespace("flags", description="Endpoint to retrieve Flags")


@flags_namespace.route("")
class FlagList(Resource):
    @admins_only
    def get(self):
        flags = Flags.query.all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = FlagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@flags_namespace.route("/types", defaults={"type_name": None})
@flags_namespace.route("/types/<type_name>")
class FlagTypes(Resource):
    @admins_only
    def get(self, type_name):
        if type_name:
            flag_class = get_flag_class(type_name)
            response = {"name": flag_class.name, "templates": flag_class.templates}
            return {"success": True, "data": response}
        else:
            response = {}
            for class_id in FLAG_CLASSES:
                flag_class = FLAG_CLASSES.get(class_id)
                response[class_id] = {
                    "name": flag_class.name,
                    "templates": flag_class.templates,
                }
            return {"success": True, "data": response}


@flags_namespace.route("/<flag_id>")
class Flag(Resource):
    @admins_only
    def get(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        response = schema.dump(flag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["templates"] = get_flag_class(flag.type).templates

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()

        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        return {"success": True}

    @admins_only
    def patch(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=flag, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
