from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.constants import RawEnum
from CTFd.models import Brackets, db
from CTFd.schemas.brackets import BracketSchema
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers.models import build_model_filters

brackets_namespace = Namespace("brackets", description="Endpoint to retrieve Brackets")


@brackets_namespace.route("")
class BracketList(Resource):
    @validate_args(
        {
            "name": (str, None),
            "description": (str, None),
            "type": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "BracketFields",
                    {"name": "name", "description": "description", "type": "type"},
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Brackets, query=q, field=field)

        brackets = Brackets.query.filter_by(**query_args).filter(*filters).all()
        schema = BracketSchema(many=True)
        response = schema.dump(brackets)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = BracketSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@brackets_namespace.route("/<int:bracket_id>")
class Bracket(Resource):
    @admins_only
    def patch(self, bracket_id):
        bracket = Brackets.query.filter_by(id=bracket_id).first_or_404()
        schema = BracketSchema()

        req = request.get_json()

        response = schema.load(req, session=db.session, instance=bracket)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, bracket_id):
        bracket = Brackets.query.filter_by(id=bracket_id).first_or_404()
        db.session.delete(bracket)
        db.session.commit()
        db.session.close()

        return {"success": True}
