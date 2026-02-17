from typing import List

from flask import abort, request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.cache import clear_challenges, clear_standings, clear_user_session
from CTFd.constants import RawEnum
from CTFd.models import (
    Awards,
    Notifications,
    Solves,
    Submissions,
    Tracking,
    Unlocks,
    Users,
    UsersMFA,
    db,
)
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.users import UserSchema
from CTFd.utils.challenges import get_submissions_for_user_id_for_challenge_id
from CTFd.utils.config import get_config, get_mail_provider
from CTFd.utils.crypto import verify_password
from CTFd.utils.decorators import admins_only, authed_only, ratelimit
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.email import sendmail, user_created_notification
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.security.auth import update_user
from CTFd.utils.security.mfa import (
    build_totp_uri,
    consume_backup_code,
    count_backup_codes,
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_backup_codes,
    generate_totp_qrcode,
    generate_totp_secret,
    get_mfa_labels,
    hash_backup_codes,
    verify_totp_code,
)
from CTFd.utils.user import get_current_user, get_current_user_type, is_admin

users_namespace = Namespace("users", description="Endpoint to retrieve Users")


UserModel = sqlalchemy_to_pydantic(Users)
TransientUserModel = sqlalchemy_to_pydantic(Users, exclude=["id"])


class UserDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: UserModel


class UserListSuccessResponse(PaginatedAPIListSuccessResponse):
    data: List[UserModel]


users_namespace.schema_model(
    "UserDetailedSuccessResponse", UserDetailedSuccessResponse.apidoc()
)

users_namespace.schema_model(
    "UserListSuccessResponse", UserListSuccessResponse.apidoc()
)


@users_namespace.route("")
class UserList(Resource):
    @check_account_visibility
    @users_namespace.doc(
        description="Endpoint to get User objects in bulk",
        responses={
            200: ("Success", "UserListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "affiliation": (str, None),
            "country": (str, None),
            "bracket": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "UserFields",
                    {
                        "name": "name",
                        "website": "website",
                        "country": "country",
                        "bracket": "bracket",
                        "affiliation": "affiliation",
                        "email": "email",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))

        if field == "email":
            if is_admin() is False:
                return {
                    "success": False,
                    "errors": {"field": "Emails can only be queried by admins"},
                }, 400

        filters = build_model_filters(model=Users, query=q, field=field)

        if is_admin() and request.args.get("view") == "admin":
            users = (
                Users.query.filter_by(**query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100, error_out=False)
            )
        else:
            users = (
                Users.query.filter_by(banned=False, hidden=False, **query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100, error_out=False)
            )

        response = UserSchema(view="user", many=True).dump(users.items)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "meta": {
                "pagination": {
                    "page": users.page,
                    "next": users.next_num,
                    "prev": users.prev_num,
                    "pages": users.pages,
                    "per_page": users.per_page,
                    "total": users.total,
                }
            },
            "success": True,
            "data": response.data,
        }

    @admins_only
    @users_namespace.doc(
        description="Endpoint to create a User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
        params={
            "notify": "Whether to send the created user an email with their credentials"
        },
    )
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
        clear_challenges()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}


@users_namespace.route("/<int:user_id>")
@users_namespace.param("user_id", "User ID")
class UserPublic(Resource):
    @check_account_visibility
    @users_namespace.doc(
        description="Endpoint to get a specific User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()

        if (user.banned or user.hidden) and is_admin() is False:
            abort(404)

        user_type = get_current_user_type(fallback="user")
        response = UserSchema(view=user_type).dump(user)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["place"] = user.place
        response.data["score"] = user.score

        return {"success": True, "data": response.data}

    @admins_only
    @users_namespace.doc(
        description="Endpoint to edit a specific User object",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, user_id):
        user = Users.query.filter_by(id=user_id).first_or_404()
        data = request.get_json()
        data["id"] = user_id

        # Admins should not be able to ban themselves
        if data["id"] == session["id"] and (
            data.get("banned") is True or data.get("banned") == "true"
        ):
            return (
                {"success": False, "errors": {"id": "You cannot ban yourself"}},
                400,
            )

        schema = UserSchema(view="admin", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        # This generates the response first before actually changing the type
        # This avoids an error during User type changes where we change
        # the polymorphic identity resulting in an ObjectDeletedError
        # https://github.com/CTFd/CTFd/issues/1794
        response = schema.dump(response.data)

        reset_mfa = data.pop("reset_mfa", "false") == "true"
        if user.mfa and reset_mfa:
            db.session.delete(user.mfa)

        db.session.commit()
        db.session.close()

        clear_user_session(user_id=user_id)
        clear_standings()
        clear_challenges()

        return {"success": True, "data": response.data}

    @admins_only
    @users_namespace.doc(
        description="Endpoint to delete a specific User object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, user_id):
        # Admins should not be able to delete themselves
        if user_id == session["id"]:
            return (
                {"success": False, "errors": {"id": "You cannot delete yourself"}},
                400,
            )

        Notifications.query.filter_by(user_id=user_id).delete()
        Awards.query.filter_by(user_id=user_id).delete()
        Unlocks.query.filter_by(user_id=user_id).delete()
        Submissions.query.filter_by(user_id=user_id).delete()
        Solves.query.filter_by(user_id=user_id).delete()
        Tracking.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
        db.session.close()

        clear_user_session(user_id=user_id)
        clear_standings()
        clear_challenges()

        return {"success": True}


@users_namespace.route("/me")
class UserPrivate(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to get the User object for the current user",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        user = get_current_user()
        response = UserSchema("self").dump(user).data

        # A user can always calculate their score regardless of any setting because they can simply sum all of their challenges
        # Therefore a user requesting their private data should be able to get their own current score
        # However place is not something that a user can ascertain on their own so it is always gated behind freeze time
        response["place"] = user.place
        response["score"] = user.get_score(admin=True)

        return {"success": True, "data": response}

    @authed_only
    @users_namespace.doc(
        description="Endpoint to edit the User object for the current user",
        responses={
            200: ("Success", "UserDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self):
        user = get_current_user()
        data = request.get_json()
        schema = UserSchema(view="self", instance=user, partial=True)
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        # Update user's session for the new session hash
        update_user(user)

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()
        clear_challenges()

        return {"success": True, "data": response.data}


@users_namespace.route("/me/mfa")
class UserPrivateMFA(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to get MFA status for the current user",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        user = get_current_user()
        mfa = UsersMFA.query.filter_by(user_id=user.id, enabled=True).first()

        if mfa:
            session.pop("mfa_enroll_secret", None)
            return {
                "success": True,
                "data": {
                    "enabled": True,
                    "enrolling": False,
                    "backup_remaining": count_backup_codes(mfa.backup_codes),
                },
            }

        mfa_qrcode = None
        mfa_secret = session.get("mfa_enroll_secret")
        if mfa_secret:
            issuer, account_name = get_mfa_labels(user)
            mfa_uri = build_totp_uri(
                secret=mfa_secret,
                account_name=account_name,
                issuer_name=issuer,
            )
            mfa_qrcode = generate_totp_qrcode(mfa_uri)

        return {
            "success": True,
            "data": {
                "enabled": False,
                "enrolling": bool(mfa_secret),
                "backup_remaining": 0,
                "secret": mfa_secret,
                "qrcode": mfa_qrcode,
            },
        }


@users_namespace.route("/me/mfa/setup")
class UserPrivateMFASetup(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to begin MFA setup for the current user",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        user = get_current_user()
        mfa = UsersMFA.query.filter_by(user_id=user.id, enabled=True).first()
        if mfa:
            return {
                "success": False,
                "errors": {
                    "setup": "Multi-factor authentication is already enabled",
                },
            }, 400

        session["mfa_enroll_secret"] = generate_totp_secret()
        mfa_secret = session.get("mfa_enroll_secret")

        mfa_qrcode = None
        if mfa_secret:
            issuer, account_name = get_mfa_labels(user)
            mfa_uri = build_totp_uri(
                secret=mfa_secret,
                account_name=account_name,
                issuer_name=issuer,
            )
            mfa_qrcode = generate_totp_qrcode(mfa_uri)

        return {
            "success": True,
            "data": {
                "enrolling": True,
                "secret": mfa_secret,
                "qrcode": mfa_qrcode,
            },
        }

    @authed_only
    @users_namespace.doc(
        description="Endpoint to cancel MFA setup for the current user",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self):
        session.pop("mfa_enroll_secret", None)

        return {
            "success": True,
            "data": {
                "enrolling": False,
            },
        }


@users_namespace.route("/me/mfa/enable")
class UserPrivateMFAEnable(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to enable MFA for the current user",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        user = get_current_user()
        data = request.get_json(silent=True) or {}
        otp = data.get("mfa_code", "")

        mfa = UsersMFA.query.filter_by(user_id=user.id, enabled=True).first()
        if mfa:
            return {
                "success": False,
                "errors": {
                    "enable": "Multi-factor authentication is already enabled",
                },
            }, 400

        if user.password is not None:
            confirm_password = data.get("confirm", "")

            if not confirm_password:
                return {
                    "success": False,
                    "errors": {"confirm": "Please confirm your current password"},
                }, 400

            if not verify_password(confirm_password, user.password):
                return {
                    "success": False,
                    "errors": {"confirm": "Your previous password is incorrect"},
                }, 400

        mfa_secret = session.get("mfa_enroll_secret")
        if not mfa_secret:
            return {
                "success": False,
                "errors": {
                    "setup": "Start MFA setup before verifying an authenticator code",
                },
            }, 400

        if verify_totp_code(secret=mfa_secret, otp=otp) is False:
            return {
                "success": False,
                "errors": {
                    "mfa_code": "The authenticator code is incorrect. Please try again.",
                },
            }, 400

        backup_codes = generate_backup_codes()
        encrypted_secret = encrypt_totp_secret(mfa_secret)
        hashed_codes = hash_backup_codes(backup_codes)

        if user.mfa:
            user.mfa.enabled = True
            user.mfa.totp_secret = encrypted_secret
            user.mfa.backup_codes = hashed_codes
            user.mfa.last_used = None
        else:
            user.mfa = UsersMFA(
                user_id=user.id,
                enabled=True,
                totp_secret=encrypted_secret,
                backup_codes=hashed_codes,
            )

        db.session.commit()
        session.pop("mfa_enroll_secret", None)

        return {
            "success": True,
            "data": {
                "enabled": True,
                "enrolling": False,
                "backup_remaining": len(backup_codes),
                "backup_codes": backup_codes,
            },
        }


@users_namespace.route("/me/mfa/disable")
class UserPrivateMFADisable(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to disable MFA for the current user",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        user = get_current_user()
        data = request.get_json(silent=True) or {}

        otp = data.get("mfa_code", "")
        backup_code = data.get("mfa_backup_code", "")
        confirm_password = data.get("confirm", "")

        mfa = UsersMFA.query.filter_by(user_id=user.id, enabled=True).first()
        if not mfa:
            return {
                "success": False,
                "errors": {"disable": "Multi-factor authentication is not enabled"},
            }, 400

        if user.password is not None:
            if not confirm_password:
                return {
                    "success": False,
                    "errors": {"confirm": "Please confirm your current password"},
                }, 400

            if not verify_password(confirm_password, user.password):
                return {
                    "success": False,
                    "errors": {"confirm": "Your previous password is incorrect"},
                }, 400

        try:
            secret = decrypt_totp_secret(mfa.totp_secret)
            verified = verify_totp_code(secret=secret, otp=otp)
        except Exception:
            verified = False

        if verified is False:
            used_backup, new_codes = consume_backup_code(
                backup_codes=mfa.backup_codes,
                candidate=backup_code,
            )

            if used_backup:
                mfa.backup_codes = new_codes
                verified = True

        if verified is False:
            return {
                "success": False,
                "errors": {
                    "mfa_code": "The authenticator or backup code is incorrect. Please try again.",
                },
            }, 400

        db.session.delete(mfa)
        db.session.commit()

        session.pop("mfa_enroll_secret", None)
        session.pop("mfa_pending", None)
        session["mfa_verified"] = True

        return {
            "success": True,
            "data": {
                "enabled": False,
                "enrolling": False,
                "backup_remaining": 0,
            },
        }


@users_namespace.route("/me/mfa/backup")
class UserPrivateMFABackup(Resource):
    @authed_only
    @users_namespace.doc(
        description="Endpoint to regenerate MFA backup codes for the current user",
        responses={
            200: ("Success", "APISimpleSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        user = get_current_user()
        data = request.get_json(silent=True) or {}
        otp = data.get("mfa_code", "")

        mfa = UsersMFA.query.filter_by(user_id=user.id, enabled=True).first()
        if not mfa:
            return {
                "success": False,
                "errors": {
                    "backup": "Enable multi-factor authentication before generating backup codes",
                },
            }, 400

        confirm_password = data.get("confirm", "")
        if user.password is not None:
            if not confirm_password:
                return {
                    "success": False,
                    "errors": {"confirm": "Please confirm your current password"},
                }, 400

            if not verify_password(confirm_password, user.password):
                return {
                    "success": False,
                    "errors": {"confirm": "Your previous password is incorrect"},
                }, 400

        try:
            secret = decrypt_totp_secret(mfa.totp_secret)
            verified = verify_totp_code(secret=secret, otp=otp)
        except Exception:
            verified = False

        if verified is False:
            return {
                "success": False,
                "errors": {
                    "mfa_code": "The authenticator code is incorrect. Please try again.",
                },
            }, 400

        backup_codes = generate_backup_codes()
        mfa.backup_codes = hash_backup_codes(backup_codes)
        db.session.commit()

        return {
            "success": True,
            "data": {
                "backup_remaining": len(backup_codes),
                "backup_codes": backup_codes,
            },
        }


@users_namespace.route("/me/submissions")
class UserPrivateSubmissions(Resource):
    @authed_only
    def get(self):
        # TODO: CTFd 4.0 Self viewing submissions should not be enabled by default until further notice
        if bool(get_config("view_self_submissions")) is False:
            abort(403)
        user = get_current_user()
        challenge_id = request.args.get("challenge_id")
        response = get_submissions_for_user_id_for_challenge_id(
            user_id=user.id, challenge_id=challenge_id
        )

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


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

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/me/fails")
class UserPrivateFails(Resource):
    @authed_only
    def get(self):
        user = get_current_user()
        fails = user.get_fails(admin=True)

        view = "user" if not is_admin() else "admin"

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            response = SubmissionSchema(view=view, many=True).dump(fails)
            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []

        count = len(fails)
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

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


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

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


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

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            response = SubmissionSchema(view=view, many=True).dump(fails)
            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []

        count = len(fails)
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

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@users_namespace.route("/<int:user_id>/email")
@users_namespace.param("user_id", "User ID")
class UserEmails(Resource):
    @admins_only
    @users_namespace.doc(
        description="Endpoint to email a User object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
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

        if result is True:
            return {"success": True}
        else:
            return (
                {"success": False, "errors": {"": [response]}},
                400,
            )
