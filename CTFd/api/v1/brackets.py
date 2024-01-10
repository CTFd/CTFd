from flask import abort, request
from flask_restx import Namespace, Resource

from CTFd.models import Brackets, db
from CTFd.schemas.brackets import BracketSchema
from CTFd.utils import get_config
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.utils.social import get_social_share
from CTFd.utils.user import get_current_user_attrs

brackets_namespace = Namespace("brackets", description="Endpoint to retrieve Brackets")


@brackets_namespace.route("")
class BracketList(Resource):
    def get(self):
        brackets = Brackets.query.all()
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
        