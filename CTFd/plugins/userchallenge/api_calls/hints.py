

from flask import request
from CTFd.models import HintUnlocks, Hints
from CTFd.plugins.userchallenge.utils import userChallenge_allowed
from CTFd.schemas.hints import HintSchema
from CTFd.models import db
from CTFd.utils.user import get_current_user, is_admin


def load(app):
    @app.route('/userchallenge/api/challenges/<challenge_id>/hints',methods=['GET'])
    def getHints(challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)
        response = schema.dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints',methods=['POST'])
    @userChallenge_allowed
    def createHint():
        req = request.get_json()
        schema = HintSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['GET'])
    def getHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        user = get_current_user()

        # We allow public accessing of hints if challenges are visible and there is no cost or prerequisites
        # If there is a cost or a prereq we should block the user from seeing the hint
        if user is None:
            if hint.cost or hint.prerequisites:
                return (
                    {
                        "success": False,
                        "errors": {"cost": ["You must login to unlock this hint"]},
                    },
                    403,
                )

        if hint.prerequisites:
            requirements = hint.prerequisites

            # Get the IDs of all hints that the user has unlocked
            all_unlocks = HintUnlocks.query.filter_by(account_id=user.account_id).all()
            unlock_ids = {unlock.target for unlock in all_unlocks}

            # Get the IDs of all free hints
            free_hints = Hints.query.filter_by(cost=0).all()
            free_ids = {h.id for h in free_hints}

            # Add free hints to unlocked IDs
            unlock_ids.update(free_ids)

            # Filter out hint IDs that don't exist
            all_hint_ids = {h.id for h in Hints.query.with_entities(Hints.id).all()}
            prereqs = set(requirements).intersection(all_hint_ids)

            # If the user has the necessary unlocks or is admin we should allow them to view
            if unlock_ids >= prereqs or is_admin():
                pass
            else:
                return (
                    {
                        "success": False,
                        "errors": {
                            "requirements": [
                                "You must unlock other hints before accessing this hint"
                            ]
                        },
                    },
                    403,
                )

        view = "unlocked"
        if hint.cost:
            view = "locked"
            unlocked = HintUnlocks.query.filter_by(
                account_id=user.account_id, target=hint.id
            ).first()
            if unlocked:
                view = "unlocked"

        if is_admin():
            if request.args.get("preview", False):
                view = "admin"

        response = HintSchema(view=view).dump(hint)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['PATCH'])
    @userChallenge_allowed
    def patchHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        req = request.get_json()

        schema = HintSchema(view="admin")
        response = schema.load(req, instance=hint, partial=True, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        db.session.delete(hint)
        db.session.commit()
        db.session.close()

        return {"success": True}
