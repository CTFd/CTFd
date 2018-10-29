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
        file_type = request.args.get('type')
        files = Files.query.filter_by(type=file_type).all()
        schema = FileSchema(many=True)
        response = schema.dump(files)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def post(self):
        files = request.files.getlist('file')
        # challenge_id
        # page_id

        objs = []
        for f in files:
            # uploads.upload_file(file=f, chalid=req.get('challenge'))
            obj = uploads.upload_file(file=f, **request.form.to_dict())
            objs.append(obj)

        schema = FileSchema(many=True)
        response = schema.dump(objs)

        if response.errors:
            return {
                'success': False,
                'errors': response.errorss
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@files_namespace.route('/<file_id>')
class FilesDetail(Resource):
    @admins_only
    def get(self, file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()
        schema = FileSchema()
        response = schema.dump(f)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()

        db.session.delete(f)
        db.session.commit()
        db.session.close()

        return {
            'success': True,
        }
