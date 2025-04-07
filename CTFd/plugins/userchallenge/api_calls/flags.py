

from CTFd.models import Flags,db
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.flags import FLAG_CLASSES, get_flag_class
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.flags import FlagSchema
from flask import render_template,request

def load(app):
    @app.route('/userchallenge/api/challenges/types')
    @userChallenge_allowed
    def typeget():
        response = {}

        for class_id in CHALLENGE_CLASSES:
            challenge_class = CHALLENGE_CLASSES.get(class_id)
            response[challenge_class.id] = {
                "id": challenge_class.id,
                "name": challenge_class.name,
                "templates": challenge_class.templates,
                "scripts": challenge_class.scripts,
                "create": render_template(
                    challenge_class.templates["create"].lstrip("admin/challenges/")
                ),
            }

        return {"success": True, "data": response}
    ## flag saving
    @app.route('/userchallenge/api/challenges/<challenge_id>/flags',methods=['GET'])
    def flagget(challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data} 
    ## flag posting
    @app.route('/userchallenge/api/flags',methods=['POST'])
    @userChallenge_allowed
    def flagpost():
        req = request.get_json()
        schema = FlagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/types',methods=['GET'])
    @userChallenge_allowed
    def flagTypeGet():
        response = {}
        for class_id in FLAG_CLASSES:
            flag_class = FLAG_CLASSES.get(class_id)
            response[class_id] = {
                "name": flag_class.name,
                "templates": flag_class.templates,
            }
        return {"success": True, "data": response}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['GET'])
    def flagIDget(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        response = schema.dump(flag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["templates"] = get_flag_class(flag.type).templates

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['PATCH'])
    @userChallenge_allowed
    def flagIDpatch(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=flag, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['DELETE'])
    @userChallenge_allowed
    def flagIDdelete(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()

        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        return {"success": True}
