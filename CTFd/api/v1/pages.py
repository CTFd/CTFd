from flask import request
from flask_restx import Namespace, Resource, fields

from CTFd.cache import clear_pages
from CTFd.models import Pages, db
from CTFd.schemas.pages import JSONPageSchema, PageSchema
from CTFd.utils.decorators import admins_only

pages_namespace = Namespace("pages", description="Endpoint to retrieve Pages")
PageModel = pages_namespace.model(
    "PageModel",
    {
        "success": fields.Boolean,
        "data": fields.Nested(
            pages_namespace.schema_model(PageSchema.__name__, JSONPageSchema)
        ),
    },
)
PageErrorModel = pages_namespace.model(
    "PageErrorModel", {"success": fields.Boolean, "errors": fields.List(fields.String)}
)


@pages_namespace.route("")
@pages_namespace.response(200, "Success")
@pages_namespace.response(400, "An error occured processing your data")
class PageList(Resource):
    @admins_only
    def get(self):
        pages = Pages.query.all()
        schema = PageSchema(exclude=["content"], many=True)
        response = schema.dump(pages)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def post(self):
        req = request.get_json()
        schema = PageSchema()
        response = schema.load(req)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_pages()

        return {"success": True, "data": response.data}

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, create_model
from pydantic.main import ModelMetaclass
from functools import wraps


def test(spec, location):
    if isinstance(spec, dict):
        spec = create_model("", **spec)

    props = spec.schema()["properties"]
    required = spec.schema()["required"]
    for k in props:
        if k in required:
            props[k]["required"] = True
        props[k]["in"] = location

    def dec(f):
        apidoc = getattr(f, "__apidoc__", {"params": {}})
        apidoc["params"].update(props)
        f.__apidoc__ = apidoc
        print(f.__apidoc__)

        params = getattr(f , "params", {})
        params[location] = spec
        f.params = params

        @wraps(f)
        def wrapper(*args, **kwargs):
            print(spec)
            loaded = spec(**request.args).dict()
            return f(*args, loaded, **kwargs)

        return wrapper
    return dec


@pages_namespace.route("/<page_id>")
@pages_namespace.response(200, "Success", PageModel)
@pages_namespace.response(
    400, "An error occured processing the provided or stored data", PageErrorModel
)
@pages_namespace.doc(params={"page_id": "ID of a page object"})
class PageDetail(Resource):

    class User(BaseModel):
        id: int
        name: str = 'user'

    @admins_only
    @pages_namespace.doc(description="Endpoint to read a page object")
    @pages_namespace.response(200, "Success", PageModel)
    @test(User, "query")
    def get(self, argsj, argsq, page_id):
        print(argsj)
        print(argsq)
        page = Pages.query.filter_by(id=page_id).first_or_404()
        schema = PageSchema()
        response = schema.dump(page)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @pages_namespace.doc(description="Endpoint to edit a page object")
    def patch(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        req = request.get_json()

        schema = PageSchema(partial=True)
        response = schema.load(req, instance=page, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_pages()

        return {"success": True, "data": response.data}

    @admins_only
    @pages_namespace.doc(description="Endpoint to delete a page object")
    def delete(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        db.session.delete(page)
        db.session.commit()
        db.session.close()

        clear_pages()

        return {"success": True}
