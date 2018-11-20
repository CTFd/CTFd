from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Configs
from CTFd.schemas.config import ConfigSchema
from CTFd.utils.decorators import (
    admins_only
)
from CTFd.utils import get_config, set_config
from CTFd.cache import clear_config, clear_standings

configs_namespace = Namespace('configs', description="Endpoint to retrieve Configs")


@configs_namespace.route('')
class ConfigList(Resource):
    @admins_only
    def get(self):
        configs = Configs.query.all()
        schema = ConfigSchema(many=True)
        response = schema.dump(configs)
        if response.errors:
            return {
                'success': False,
                'errors': response.errors,
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def post(self):
        req = request.get_json()
        schema = ConfigSchema()
        response = schema.load(req)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_config()
        clear_standings()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def patch(self):
        req = request.get_json()

        for key, value in req.items():
            set_config(key=key, value=value)

        clear_config()
        clear_standings()

        return {
            'success': True
        }


@configs_namespace.route('/<config_key>')
class Config(Resource):
    @admins_only
    def get(self, config_key):

        return {
            'success': True,
            'data': get_config(config_key)
        }

    @admins_only
    def patch(self, config_key):
        config = Configs.query.filter_by(key=config_key).first()
        data = request.get_json()
        if config:
            schema = ConfigSchema(instance=config, partial=True)
            response = schema.load(data)
        else:
            schema = ConfigSchema()
            data['key'] = config_key
            response = schema.load(data)
            db.session.add(response.data)

        if response.errors:
            return response.errors, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_config()
        clear_standings()

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()

        db.session.delete(config)
        db.session.commit()
        db.session.close()

        clear_config()
        clear_standings()

        return {
            'success': True,
        }
