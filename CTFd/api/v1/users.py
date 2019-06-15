from flask import session, request, abort
from flask_restplus import Namespace, Resource
from CTFd.models import (
    db,
    Users,
    Solves,
    Awards,
    Tracking,
    Unlocks,
    Submissions,
    Notifications,
)
from CTFd.utils.decorators import authed_only, admins_only, ratelimit
from CTFd.cache import clear_standings
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email import sendmail, user_created_notification
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)

from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.users import UserSchema


users_namespace = Namespace("users", description="Endpoint to retrieve Users")


@users_namespace.route("")
class UserList(Resource):
    @check_account_visibility
    def get(self):
        users = Users.query.filter_by(banned=False, hidden=False)
        response = UserSchema(view="user", many=True).dump(users)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    @users_namespace.doc(
        params={
            "notify": "Whether to send the created user an email with their credentials"
        }
    )
    @admins_only
    def post(self):
        req = request.get_json()
        schema = UserSchema("admin")
        response = schema.load(req)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        if request.args.get("notify"):
            name = response.data.name
            email = response.data.email
            password = req.get("password")

            user_created_notification(addr=email, name=name, password=password)

        clear_standings()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}


@users_namespace.route("/<int:user_id>")
@users_namespace.param("user_id", "User ID")
class UserPublic(Resource):
    @check_account_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)

        response = UserSchema(view=session.get("type", "user")).dump(user)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["place"] = user.place
        response.data["score"] = user.score

        return {"success": True, "data": response.data}

    @admins_only
    def patch(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()
        data = request.get_json()
        data["id"] = user_id
        schema = UserSchema(view="admin", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)

        db.session.close()

        clear_standings()

        return {"success": True, "data": response}

    @admins_only
    def delete(self, user_id):
        Notifications.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Unlocks.query.filter_by(user_id=user_id).delete()
        Submissions.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
        db.session.close()

        clear_standings()

        return {"success": True}


@users_namespace.route("/me")
class UserPrivate(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        response = UserSchema("self").dump(user).data
        response["place"] = user.place
        response["score"] = user.score
        return {"success": True, "data": response}

    @authed_only
    def patch(self):
        user = get_current_user()
        data = request.get_json()
        schema = UserSchema(view="self", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()

        return {"success": True, "data": response.data}


@users_namespace.route("/me/solves")
class UserPrivateSolves(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        solves = user.get_solves(admin=True)

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@users_namespace.route("/me/fails")
class UserPrivateFails(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        fails = user.get_fails(admin=True)

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(fails)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        if is_admin():
            data = response.data
        else:
            data = []
        count = len(response.data)

        return {"success": True, "data": data, "meta": {"count": count}}


@users_namespace.route("/me/awards")
@users_namespace.param("user_id", "User ID")
class UserPrivateAwards(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        awards = user.get_awards(admin=True)

        view = "user" if not is_admin() else "admin"
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@users_namespace.route("/<user_id>/solves")
@users_namespace.param("user_id", "User ID")
class UserPublicSolves(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)

        solves = user.get_solves(admin=is_admin())

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@users_namespace.route("/<user_id>/fails")
@users_namespace.param("user_id", "User ID")
class UserPublicFails(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)
        fails = user.get_fails(admin=is_admin())

        view = "user" if not is_admin() else "admin"
        response = SubmissionSchema(view=view, many=True).dump(fails)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        if is_admin():
            data = response.data
        else:
            data = []
        count = len(response.data)

        return {"success": True, "data": data, "meta": {"count": count}}


@users_namespace.route("/<user_id>/awards")
@users_namespace.param("user_id", "User ID or 'me'")
class UserPublicAwards(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)
        awards = user.get_awards(admin=is_admin())

        view = "user" if not is_admin() else "admin"
        response = AwardSchema(view=view, many=True).dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@users_namespace.route("/<int:user_id>/email")
@users_namespace.param("user_id", "User ID")
class UserEmails(Resource):
    @admins_only
    @ratelimit(method="POST", limit=10, interval=60)
    def post(self, user_id):
        req = request.get_json()
        text = req.get("text", "").strip()
        user = Users.query.filter_by(id=user_id).first_or_404()

        if get_mail_provider() is None:
            return (
                {"success": False, "errors": {"": ["Email settings not configured"]}},
                400,
            )

        if not text:
            return (
                {"success": False, "errors": {"text": ["Email text cannot be empty"]}},
                400,
            )

        result, response = sendmail(addr=user.email, text=text)

        return {"success": result, "data": {}}
