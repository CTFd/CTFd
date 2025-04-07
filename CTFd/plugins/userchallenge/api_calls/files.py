from CTFd.api.v1.helpers.request import validate_args
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.files import FileSchema
from CTFd.utils import uploads
from flask import request
from flask_restx import Namespace
from CTFd.models import ChallengeFiles as ChallengeFilesModel, Files,db

def load(app):
    @app.route('/userchallenge/api/challenges/<challenge_id>/files', methods=['GET'])
    def getchallengeFiles(challenge_id):
        response = []

        challenge_files = ChallengeFilesModel.query.filter_by(
            challenge_id=challenge_id
        ).all()

        for f in challenge_files:
            response.append({"id": f.id, "type": f.type, "location": f.location})
        return {"success": True, "data": response}
    files_namespace = Namespace("files", description="Endpoint to retrieve Files")
    @app.route('/userchallenge/api/files',methods=['POST'])
    @files_namespace.doc(
        description="Endpoint to get file objects in bulk",
        responses={
            200: ("Success", "FileDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
        params={
            "file": {
                "in": "formData",
                "type": "file",
                "required": True,
                "description": "The file to upload",
            }
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "challenge": (int, None),
            "page_id": (int, None),
            "page": (int, None),
            "type": (str, None),
            "location": (str, None),
        },
        location="form",
    )
    @userChallenge_allowed
    def uploadFile(form_args):
        files = request.files.getlist("file")
        location = form_args.get("location")
        # challenge_id
        # page_id

        # Handle situation where users attempt to upload multiple files with a single location
        if len(files) > 1 and location:
            return {
                "success": False,
                "errors": {
                    "location": ["Location cannot be specified with multiple files"]
                },
            }, 400

        objs = []
        for f in files:
            # uploads.upload_file(file=f, chalid=req.get('challenge'))
            try:
                obj = uploads.upload_file(file=f, **form_args)
            except ValueError as e:
                return {
                    "success": False,
                    "errors": {"location": [str(e)]},
                }, 400
            objs.append(obj)

        schema = FileSchema(many=True)
        response = schema.dump(objs)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/files/<file_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteFile(file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()

        uploads.delete_file(file_id=f.id)
        db.session.delete(f)
        db.session.commit()
        db.session.close()

        return {"success": True}
    @app.route('/userchallenge/api/files/<file_id>',methods=['GET'])
    def getFile(file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()
        schema = FileSchema()
        response = schema.dump(f)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
