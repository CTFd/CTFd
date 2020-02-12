import datetime

from flask import request, session
from flask_restplus import Namespace, Resource

from CTFd.models import Tokens, db
from CTFd.schemas.tokens import TokenSchema
from CTFd.utils.decorators import authed_only, require_verified_emails
from CTFd.utils.security.auth import generate_user_token
from CTFd.utils.user import get_current_user, is_admin

tokens_namespace = Namespace("tokens", description="Endpoint to retrieve Tokens")


@tokens_namespace.route("")
class TokenList(Resource):
    @require_verified_emails
    @authed_only
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
    @require_verified_emails
    @authed_only
    def get(self, token_id):
        if is_admin():
            token = Tokens.query.filter_by(id=token_id).first_or_404()
        else:
            token = Tokens.query.filter_by(
                id=token_id, user_id=session["id"]
            ).first_or_404()

        schema = TokenSchema(view=session.get("type", "user"))
        response = schema.dump(token)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @require_verified_emails
    @authed_only
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
