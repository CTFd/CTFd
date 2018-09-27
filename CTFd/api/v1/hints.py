from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Hints
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    admins_only
)
from sqlalchemy.sql import or_

hints_namespace = Namespace('hints', description="Endpoint to retrieve Hints")


@hints_namespace.route('')
class HintList(Resource):
    def get(self):
        pass

    @admins_only
    def post(self):
        pass


@hints_namespace.route('/<hint_id>')
class Hint(Resource):
    def get(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        return hint.get_dict()

    @admins_only
    def delete(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        db.session.delete(hint)
        db.session.commit()
        db.session.close()

        response = {
            'success': True
        }
        return response

    @admins_only
    def put(self, hint_id):
        pass