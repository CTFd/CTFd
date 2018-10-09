from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Configs
from CTFd.schemas.config import ConfigSchema
from CTFd.utils.decorators import (
    admins_only
)

configs_namespace = Namespace('configs', description="Endpoint to retrieve Configs")


@configs_namespace.route('')
class ConfigList(Resource):
    @admins_only
    def get(self):
        configs = Configs.query.all()
        schema = ConfigSchema(many=True)
        result = schema.dump(configs)
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        schema = ConfigSchema()
        config = schema.load(req, session=db.session)

        if config.errors:
            return config.errors

        db.session.add(config.data)
        db.session.commit()
        db.session.close()

        return schema.dump(config)


@configs_namespace.route('/<config_key>')
class Config(Resource):
    @admins_only
    def get(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()
        return ConfigSchema().dump(config)

    @admins_only
    def patch(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()
        data = request.get_json()
        response = ConfigSchema(instance=config, partial=True).load(data)

        if response.errors:
            return response.errors

        db.session.commit()
        response = ConfigSchema().dump(response.data)
        db.session.close()
        return response

    @admins_only
    def delete(self, config_key):
        config = Configs.query.filter_by(key=config_key).first_or_404()

        db.session.delete(config)
        db.session.commit()
        db.session.close()

        response = {
            'success': True,
        }
        return response
