

from flask import request
from CTFd.models import Tags,db
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.tags import TagSchema



def load(app):
    @app.route('/userchallenge/api/challenges/<challenge_id>/tags',methods=['GET'])
    def getTags(challenge_id):
        response = []

        tags = Tags.query.filter_by(challenge_id=challenge_id).all()

        for t in tags:
            response.append(
                {"id": t.id, "challenge_id": t.challenge_id, "value": t.value}
            )
        return {"success": True, "data": response}

    @app.route('/userchallenge/api/tags',methods=['POST'])
    @userChallenge_allowed
    def createTag():
        req = request.get_json()
        schema = TagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['GET'])
    def getTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()

        response = TagSchema().dump(tag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['PATCH'])
    @userChallenge_allowed
    def patchTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}
