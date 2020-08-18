from typing import List

from flask import request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.models import build_model_filters
from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.constants import RawEnum
from CTFd.models import Fields, db
from CTFd.schemas.fields import FieldSchema
from CTFd.utils.decorators import admins_only

fields_namespace = Namespace("fields", description="Endpoint to retrieve Fields")


@fields_namespace.route("")
class FieldList(Resource):
    @admins_only
    @validate_args(
        {
            "type": (str, None),
            "q": (str, None),
            "field": (RawEnum("FieldFields", {"description": "description"}), None),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Fields, query=q, field=field)

        fields = Fields.query.filter_by(**query_args).filter(*filters).all()
        schema = FieldSchema(many=True)

        response = schema.dump(fields)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = FieldSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}


@fields_namespace.route("/<field_id>")
class Field(Resource):
    @admins_only
    def get(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        schema = FieldSchema()

        response = schema.dump(field)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def patch(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        schema = FieldSchema()

        req = request.get_json()

        response = schema.load(req, session=db.session, instance=field)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, field_id):
        field = Fields.query.filter_by(id=field_id).first_or_404()
        db.session.delete(field)
        db.session.commit()
        db.session.close()

        return {"success": True}
