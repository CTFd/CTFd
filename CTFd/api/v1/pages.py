from typing import List

from flask import request
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.models import build_model_filters
from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import clear_pages
from CTFd.constants import RawEnum
from CTFd.models import Pages, db
from CTFd.schemas.pages import PageSchema
from CTFd.utils.decorators import admins_only

pages_namespace = Namespace("pages", description="Endpoint to retrieve Pages")


PageModel = sqlalchemy_to_pydantic(Pages)
TransientPageModel = sqlalchemy_to_pydantic(Pages, exclude=["id"])


class PageDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: PageModel


class PageListSuccessResponse(APIListSuccessResponse):
    data: List[PageModel]


pages_namespace.schema_model(
    "PageDetailedSuccessResponse", PageDetailedSuccessResponse.apidoc()
)

pages_namespace.schema_model(
    "PageListSuccessResponse", PageListSuccessResponse.apidoc()
)


@pages_namespace.route("")
@pages_namespace.doc(
    responses={200: "Success", 400: "An error occured processing your data"}
)
class PageList(Resource):
    @admins_only
    @pages_namespace.doc(
        description="Endpoint to get page objects in bulk",
        responses={
            200: ("Success", "PageListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "id": (int, None),
            "title": (str, None),
            "route": (str, None),
            "draft": (bool, None),
            "hidden": (bool, None),
            "auth_required": (bool, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "PageFields",
                    {"title": "title", "route": "route", "content": "content"},
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        filters = build_model_filters(model=Pages, query=q, field=field)

        pages = Pages.query.filter_by(**query_args).filter(*filters).all()
        schema = PageSchema(exclude=["content"], many=True)
        response = schema.dump(pages)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    @pages_namespace.doc(
        description="Endpoint to create a page object",
        responses={
            200: ("Success", "PageDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(TransientPageModel, location="json")
    def post(self, json_args):
        req = json_args
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


@pages_namespace.route("/<page_id>")
@pages_namespace.doc(
    params={"page_id": "ID of a page object"},
    responses={
        200: ("Success", "PageDetailedSuccessResponse"),
        400: (
            "An error occured processing the provided or stored data",
            "APISimpleErrorResponse",
        ),
    },
)
class PageDetail(Resource):
    @admins_only
    @pages_namespace.doc(description="Endpoint to read a page object")
    def get(self, page_id):
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
    @pages_namespace.doc(
        description="Endpoint to delete a page object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, page_id):
        page = Pages.query.filter_by(id=page_id).first_or_404()
        db.session.delete(page)
        db.session.commit()
        db.session.close()

        clear_pages()

        return {"success": True}
