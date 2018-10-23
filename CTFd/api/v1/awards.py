from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Awards
from CTFd.schemas.awards import AwardSchema
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    admins_only
)
from sqlalchemy.sql import or_

awards_namespace = Namespace('awards', description="Endpoint to retrieve Awards")


@awards_namespace.route('')
class AwardList(Resource):
    @admins_only
    def get(self):
        pass

    @admins_only
    def post(self):
        req = request.get_json()
        schema = AwardSchema()

        award = schema.load(req, session=db.session)
        if award.errors:
            return award.errors, 400
        db.session.add(award.data)
        db.session.commit()
        db.session.close()

        return schema.dump(award)


@awards_namespace.route('/<award_id>')
@awards_namespace.param('award_id', 'An Award ID')
class Award(Resource):
    @admins_only
    def get(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        return AwardSchema().dump(award)

    @admins_only
    def delete(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        db.session.delete(award)
        db.session.commit()
        db.session.close()

        response = {
            'success': True,
        }
        return response
