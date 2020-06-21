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


from webargs import fields
from webargs.flaskparser import use_args
from CTFd.schemas import JSONSchema
from webargs.dict2schema import dict2schema


def use_documented_args(*args, **kwargs):
    location = kwargs.get("location", "query")
    schema = JSONSchema(dict2schema(args[0])())["properties"]
    print(schema)

    for k in schema:
        schema[k]["in"] = location

    dec = use_args(*args, **kwargs)

    def test(f):
        doc = getattr(f, "__apidoc__", {"params": {}})
        doc["params"].update(schema)
        f.__apidoc__ = doc
        return dec(f)
    return test


@pages_namespace.route("/<page_id>")
@pages_namespace.response(200, "Success", PageModel)
@pages_namespace.response(
    400, "An error occured processing the provided or stored data", PageErrorModel
)
@pages_namespace.doc(params={"page_id": "ID of a page object"})
class PageDetail(Resource):
    @admins_only
    @pages_namespace.doc(description="Endpoint to read a page object")
    @pages_namespace.response(200, "Success", PageModel)
    @use_documented_args({"name": fields.Str(required=True)}, location="query")
    def get(self, args, page_id):
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
