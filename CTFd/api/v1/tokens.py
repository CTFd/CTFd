from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Tokens
from CTFd.utils.user import get_current_user
from CTFd.schemas.tokens import TokenSchema
from CTFd.utils.security.auth import generate_user_token
from CTFd.utils.decorators import require_verified_emails, admins_only, authed_only
import datetime

tokens_namespace = Namespace("tokens", description="Endpoint to retrieve Tokens")


@tokens_namespace.route("")
class TokenList(Resource):
    @require_verified_emails
    @authed_only
    def post(self):
        req = request.get_json()
        expiration = req.get("expiration")
        if expiration:
            expiration = datetime.datetime.strptime(expiration, "%Y-%m-%d")

        user = get_current_user()
        token = generate_user_token(user, expiration=expiration)

        # Explicitly use admin view so that user's can see the value of their token
        schema = TokenSchema(view="admin")
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@tokens_namespace.route("/<token_id>")
@tokens_namespace.param("token_id", "A Token ID")
class TokenDetail(Resource):
    @admins_only
    def get(self, token_id):
        token = Tokens.query.filter_by(id=token_id).first_or_404()

        schema = TokenSchema(view="admin")
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @require_verified_emails
    @authed_only
    def delete(self, token_id):
        token = Tokens.query.filter_by(id=token_id).first_or_404()
        db.session.delete(token)
        db.session.commit()
        db.session.close()

        return {"success": True}
