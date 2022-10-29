import json
from typing import List

from flask import request
from flask import current_app as app
from flask_restx import Namespace, Resource
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.models import Users
from CTFd.plugins.csaw.models import (
    CSAWRegions,
    get_country_region_dict,
    get_members,
    get_region,
)
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.user import get_current_user

csaw_namespace = Namespace("csaw", description="Endpoint to retrieve CSAW")


@csaw_namespace.route("/members")
class Members(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        app.logger.info(user)
        members = get_members(user)
        data = [m.asdict() for m in members]
        data = json.dumps(data)

        return {"success": True, "data": data}

    # TODO
    @authed_only
    def patch(self):
        ...


@csaw_namespace.route("/country_region_list")
class CountryRegionList(Resource):
    def get(self):
        try:
            data = get_country_region_dict()
            data = json.dumps(data)
            return {"success": True, "data": data}
        except:
            return {"success": False, "data": ""}


@csaw_namespace.route("/region")
class Region(Resource):
    def get(self, country):
        try:
            data = get_region(country)
            return {"success": True, "data": data}
        except:
            return {"success": False, "data": ""}


@csaw_namespace.route("/country_region_update")
class CountryRegioUpdate(Resource):
    def patch(self):
        try:
            req = request.get_json()
            ...
        except:
            ...
