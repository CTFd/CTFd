from flask import request
from flask_restx import Namespace, Resource

from CTFd.cache import clear_standings
from CTFd.utils.config import is_teams_mode
from CTFd.models import Awards, db, Users
from CTFd.schemas.awards import AwardSchema
from CTFd.utils.decorators import admins_only

awards_namespace = Namespace("awards", description="Endpoint to retrieve Awards")


@awards_namespace.route("")
class AwardList(Resource):
    @admins_only
    def post(self):
        req = request.get_json()

        # Force a team_id if in team mode and unspecified
        if is_teams_mode():
            team_id = req.get("team_id")
            if team_id is None:
                user = Users.query.filter_by(id=req["user_id"]).first()
                if user.team_id is None:
                    return (
                        {
                            "success": False,
                            "errors": {
                                "team_id": [
                                    "User doesn't have a team to associate award with"
                                ]
                            },
                        },
                        400,
                    )
                req["team_id"] = user.team_id

        schema = AwardSchema()

        response = schema.load(req, session=db.session)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        # Delete standings cache because awards can change scores
        clear_standings()

        return {"success": True, "data": response.data}


@awards_namespace.route("/<award_id>")
@awards_namespace.param("award_id", "An Award ID")
class Award(Resource):
    @admins_only
    def get(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        response = AwardSchema().dump(award)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, award_id):
        award = Awards.query.filter_by(id=award_id).first_or_404()
        db.session.delete(award)
        db.session.commit()
        db.session.close()

        # Delete standings cache because awards can change scores
        clear_standings()

        return {"success": True}
