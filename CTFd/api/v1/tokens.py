import datetime
from typing import List

from flask import request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.models import Tokens, db
from CTFd.schemas.tokens import TokenSchema
from CTFd.utils.decorators import authed_only, require_verified_emails
from CTFd.utils.security.auth import generate_user_token
from CTFd.utils.user import get_current_user, get_current_user_type, is_admin

tokens_namespace = Namespace("tokens", description="Endpoint to retrieve Tokens")

TokenModel = sqlalchemy_to_pydantic(Tokens)
ValuelessTokenModel = sqlalchemy_to_pydantic(Tokens, exclude=["value"])


class TokenDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TokenModel


class ValuelessTokenDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: ValuelessTokenModel


class TokenListSuccessResponse(APIListSuccessResponse):
    data: List[TokenModel]


tokens_namespace.schema_model(
    "TokenDetailedSuccessResponse", TokenDetailedSuccessResponse.apidoc()
)

tokens_namespace.schema_model(
    "ValuelessTokenDetailedSuccessResponse",
    ValuelessTokenDetailedSuccessResponse.apidoc(),
)

tokens_namespace.schema_model(
    "TokenListSuccessResponse", TokenListSuccessResponse.apidoc()
)


@tokens_namespace.route("")
class TokenList(Resource):
    @require_verified_emails
    @authed_only
    @tokens_namespace.doc(
        description="Endpoint to get token objects in bulk",
        responses={
            200: ("Success", "TokenListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        user = get_current_user()
        tokens = Tokens.query.filter_by(user_id=user.id)
        response = TokenSchema(view=["id", "type", "expiration"], many=True).dump(
            tokens
        )

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @require_verified_emails
    @authed_only
    @tokens_namespace.doc(
        description="Endpoint to create a token object",
        responses={
            200: ("Success", "TokenDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        expiration = req.get("expiration")
        description = req.get("description")
        if expiration:
            expiration = datetime.datetime.strptime(expiration, "%Y-%m-%d")

        user = get_current_user()
        token = generate_user_token(
            user, expiration=expiration, description=description
        )

        # Explicitly use admin view so that user's can see the value of their token
        schema = TokenSchema(view="admin")
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@tokens_namespace.route("/<token_id>")
@tokens_namespace.param("token_id", "A Token ID")
class TokenDetail(Resource):
    @require_verified_emails
    @authed_only
    @tokens_namespace.doc(
        description="Endpoint to get an existing token object",
        responses={
            200: ("Success", "ValuelessTokenDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, token_id):
        if is_admin():
            token = Tokens.query.filter_by(id=token_id).first_or_404()
        else:
            token = Tokens.query.filter_by(
                id=token_id, user_id=session["id"]
            ).first_or_404()

        user_type = get_current_user_type(fallback="user")
        schema = TokenSchema(view=user_type)
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @require_verified_emails
    @authed_only
    @tokens_namespace.doc(
        description="Endpoint to delete an existing token object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, token_id):
        if is_admin():
            token = Tokens.query.filter_by(id=token_id).first_or_404()
        else:
            user = get_current_user()
            token = Tokens.query.filter_by(id=token_id, user_id=user.id).first_or_404()
        db.session.delete(token)
        db.session.commit()
        db.session.close()

        return {"success": True}
