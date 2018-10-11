from flask import request
from flask_restplus import Namespace, Resource
from CTFd.models import db, Files, ChallengeFiles, PageFiles
from CTFd.schemas.files import FileSchema
from CTFd.utils import uploads
from CTFd.utils.decorators import (
    admins_only
)

files_namespace = Namespace('files', description="Endpoint to retrieve Files")


@files_namespace.route('')
class FilesList(Resource):
    @admins_only
    def get(self):
        files = Files.query.all()
        schema = FileSchema(many=True)
        result = schema.dump(files)
        return result.data

    @admins_only
    def post(self):
        req = request.get_json()
        files = request.files.getlist('files[]')

        for f in files:
            uploads.upload_file(file=f, chalid=req.get('challenge'))

        db.session.commit()
        db.session.close()
        schema = FileSchema()
        config = schema.load(req, session=db.session)

        if config.errors:
            return config.errors

        db.session.add(config.data)
        db.session.commit()
        db.session.close()

        return schema.dump(config)


@files_namespace.route('/<file_id>')
class FilesDetail(Resource):
    @admins_only
    def get(self, file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()
        return FileSchema().dump(f)

    # @admins_only
    # def patch(self, config_key):
    #     config = Configs.query.filter_by(key=config_key).first_or_404()
    #     data = request.get_json()
    #     response = ConfigSchema(instance=config, partial=True).load(data)
    #
    #     if response.errors:
    #         return response.errors
    #
    #     db.session.commit()
    #     response = ConfigSchema().dump(response.data)
    #     db.session.close()
    #     return response
    #
    @admins_only
    def delete(self, file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()

        db.session.delete(f)
        db.session.commit()
        db.session.close()

        response = {
            'success': True,
        }
        return response
