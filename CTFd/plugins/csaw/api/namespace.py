from asyncio.log import logger
import json
from sys import exc_info
import traceback
from typing import List

import pydantic
from flask import request
from flask import current_app as app
from flask_restx import Namespace, Resource
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.models import db
from CTFd.plugins.csaw.models import (
    CSAWRegions,
    get_country_region_list,
    get_members,
    get_region,
    updated_country_region,
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
            data = get_country_region_list()
            app.logger.info(data)
            return {"success": True, "data": data}
        except Exception as e:
            app.logger.error(e)
            return {"success": False, "data": ""}


@csaw_namespace.route("/region")
class Region(Resource):
    def get(self):
        try:
            country = request.args.get("country")
            data = get_region(country)
            return {"success": True, "data": data}
        except:
            return {"success": False, "data": ""}


class CountryRegionSchema(pydantic.BaseModel):
    country: str
    region: str


@csaw_namespace.route("/country_region_update")
class CountryRegioUpdate(Resource):
    def post(self):
        try:
            req = request.get_json()
            country_region_list = pydantic.parse_obj_as(List[CountryRegionSchema], req)

            updated_models = []
            for d in country_region_list:
                _model = updated_country_region(d.country, d.region)
                updated_models.append(_model)

            app.logger.info(updated_models)

            db.session.add_all(updated_models)
            db.session.commit()
            db.session.close()
            return {"success": True, "data": req}
        except Exception as e:
            app.logger.error(e, exc_info=True)
            return {"success": False, "data": ""}
