from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Flags
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
    def get(self):
        pass

    @admins_only
    def post(self):
        challenge_id = request.form.get('challenge_id')
        content = request.form.get('flag')
        data = request.form.get('metadata')
        type = request.form.get('type')

        flag = Flag(
            challenge_id=challenge_id,
            content=content,
            data=data,
            type=type
        )
        db.session.add(flag)
        db.session.commit()
        db.session.close()

        return flag.get_dict()


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
        return flag.get_dict(admin=True)

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
