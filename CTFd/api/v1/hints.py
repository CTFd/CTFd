from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Hints
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.schemas.hints import HintSchema
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
    @admins_only
    def get(self):
        # TODO sort by challenge ID
        hints = Hints.query.all()
        result = HintSchema(many=True).dump(hints)
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        schema = HintSchema('admin')
        hint = schema.load(req, session=db.session)

        if hint.errors:
            return hint.errors, 400

        db.session.add(hint.data)
        db.session.commit()
        response = schema.dump(hint.data)

        return response


@hints_namespace.route('/<hint_id>')
class Hint(Resource):
    def get(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        view = HintSchema.views.get(session.get('type'))
        # TODO: Ensure that the requesting user can actually access the hint
        response = HintSchema(view=view).dump(hint)
        return response.data

    @admins_only
    def patch(self, hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        req = request.get_json()

        schema = HintSchema()
        hint = schema.load(req, instance=hint, partial=True, session=db.session)

        if hint.errors:
            return hint.errors, 400

        db.session.add(hint.data)
        db.session.commit()
        response = schema.dump(hint.data)
        return response

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