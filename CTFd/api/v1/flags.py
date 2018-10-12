from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Flags
from CTFd.schemas.flags import FlagSchema
from CTFd.plugins.flags import get_flag_class, FLAG_CLASSES
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
        response = schema.dump(flag)
        db.session.close()

        return response


@flags_namespace.route('/types', defaults={'type_name': None})
@flags_namespace.route('/types/<type_name>')
class FlagTypes(Resource):
    @admins_only
    def get(self, type_name):
        if type_name:
            flag_class = get_flag_class(type_name)
            response = {
                'name': flag_class.name,
                'templates': flag_class.templates
            }
            return response
        else:
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
        # TODO: Perhaps flag plugins should be similar to challenges and have CRUD methods
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        response = FlagSchema().dump(flag)
        if response.errors:
            return response.errors

        response.data['templates'] = get_flag_class(flag.type).templates
        return response.data

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
    def patch(self, flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        flag = schema.load(req, session=db.session, instance=flag, partial=True)
        if flag.errors:
            return flag.errors

        db.session.commit()
        response = schema.dump(flag.data)
        db.session.close()
        return response
