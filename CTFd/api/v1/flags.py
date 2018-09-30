from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Flags
from CTFd.schemas.flags import FlagSchema
from CTFd.plugins.flags import get_key_class, FLAG_CLASSES
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    admins_only
)
from sqlalchemy.sql import or_

flags_namespace = Namespace('flags', description="Endpoint to retrieve Flags")


@flags_namespace.route('')
class FlagList(Resource):
    @admins_only
    def get(self):
        # TODO: Sort by challenge ID
        flags = Flags.query.all()
        schema = FlagSchema(many=True)
        result = schema.dump(flags)
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        schema = FlagSchema()
        flag = schema.load(req, session=db.session)

        if flag.errors:
            return flag.errors

        db.session.add(flag.data)
        db.session.commit()
        db.session.close()

        return schema.dump(flag)


@flags_namespace.route('/types')
class FlagTypes(Resource):

    @admins_only
    def get(self):
        response = {}
        for class_id in FLAG_CLASSES:
            flag_class = FLAG_CLASSES.get(class_id)
            response[class_id] = {
                'name': flag_class.name,
                'templates': flag_class.templates,
            }
        return response


@flags_namespace.route('/<flag_id>')
class Flag(Resource):
    @admins_only
    def get(self, flag_id):
        # TODO: This should probably defer to the read method of a flag plugin
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        return FlagSchema().dump(flag)

    @admins_only
    def delete(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        response = {
            'success': True
        }
        return response

    @admins_only
    def put(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        flag = schema.load(req, session=db.session, instance=flag)
        if flag.errors:
            return flag.errors

        db.session.commit()
        response = schema.dump(flag.data)
        db.session.close()
        return response
