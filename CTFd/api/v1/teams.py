import copy
from typing import List

from flask import abort, request, session
from flask_restx import Namespace, Resource

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import (
    APIDetailedSuccessResponse,
    PaginatedAPIListSuccessResponse,
)
from CTFd.cache import (
    clear_challenges,
    clear_standings,
    clear_team_session,
    clear_user_session,
)
from CTFd.constants import RawEnum
from CTFd.models import Awards, Submissions, Teams, Unlocks, Users, db
from CTFd.schemas.awards import AwardSchema
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.schemas.teams import TeamSchema
from CTFd.utils import get_config
from CTFd.utils.decorators import admins_only, authed_only, require_team
from CTFd.utils.decorators.modes import require_team_mode
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.user import get_current_team, get_current_user_type, is_admin

teams_namespace = Namespace("teams", description="Endpoint to retrieve Teams")

TeamModel = sqlalchemy_to_pydantic(Teams)
TransientTeamModel = sqlalchemy_to_pydantic(Teams, exclude=["id"])


class TeamDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: TeamModel


class TeamListSuccessResponse(PaginatedAPIListSuccessResponse):
    data: List[TeamModel]


teams_namespace.schema_model(
    "TeamDetailedSuccessResponse", TeamDetailedSuccessResponse.apidoc()
)

teams_namespace.schema_model(
    "TeamListSuccessResponse", TeamListSuccessResponse.apidoc()
)


@teams_namespace.route("")
class TeamList(Resource):
    method_decorators = [require_team_mode]

    @check_account_visibility
    @teams_namespace.doc(
        description="Endpoint to get Team objects in bulk",
        responses={
            200: ("Success", "TeamListSuccessResponse"),
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
                    "TeamFields",
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

        filters = build_model_filters(model=Teams, query=q, field=field)

        if is_admin() and request.args.get("view") == "admin":
            teams = (
                Teams.query.filter_by(**query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100, error_out=False)
            )
        else:
            teams = (
                Teams.query.filter_by(hidden=False, banned=False, **query_args)
                .filter(*filters)
                .paginate(per_page=50, max_per_page=100, error_out=False)
            )

        user_type = get_current_user_type(fallback="user")
        view = copy.deepcopy(TeamSchema.views.get(user_type))
        view.remove("members")
        response = TeamSchema(view=view, many=True).dump(teams.items)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "meta": {
                "pagination": {
                    "page": teams.page,
                    "next": teams.next_num,
                    "prev": teams.prev_num,
                    "pages": teams.pages,
                    "per_page": teams.per_page,
                    "total": teams.total,
                }
            },
            "success": True,
            "data": response.data,
        }

    @admins_only
    @teams_namespace.doc(
        description="Endpoint to create a Team object",
        responses={
            200: ("Success", "TeamDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        req = request.get_json()
        user_type = get_current_user_type()
        view = TeamSchema.views.get(user_type)
        schema = TeamSchema(view=view)
        response = schema.load(req)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        clear_standings()
        clear_challenges()

        return {"success": True, "data": response.data}


@teams_namespace.route("/<int:team_id>")
@teams_namespace.param("team_id", "Team ID")
class TeamPublic(Resource):
    method_decorators = [require_team_mode]

    @check_account_visibility
    @teams_namespace.doc(
        description="Endpoint to get a specific Team object",
        responses={
            200: ("Success", "TeamDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        if (team.banned or team.hidden) and is_admin() is False:
            abort(404)

        user_type = get_current_user_type(fallback="user")
        view = TeamSchema.views.get(user_type)
        schema = TeamSchema(view=view)
        response = schema.dump(team)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["place"] = team.place
        response.data["score"] = team.score
        return {"success": True, "data": response.data}

    @admins_only
    @teams_namespace.doc(
        description="Endpoint to edit a specific Team object",
        responses={
            200: ("Success", "TeamDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()
        data = request.get_json()
        data["id"] = team_id

        schema = TeamSchema(view="admin", instance=team, partial=True)

        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response = schema.dump(response.data)
        db.session.commit()

        clear_team_session(team_id=team.id)
        clear_standings()
        clear_challenges()

        db.session.close()

        return {"success": True, "data": response.data}

    @admins_only
    @teams_namespace.doc(
        description="Endpoint to delete a specific Team object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()
        team_id = team.id

        for member in team.members:
            member.team_id = None
            clear_user_session(user_id=member.id)

        db.session.delete(team)
        db.session.commit()

        clear_team_session(team_id=team_id)
        clear_standings()
        clear_challenges()

        db.session.close()

        return {"success": True}


@teams_namespace.route("/me")
@teams_namespace.param("team_id", "Current Team")
class TeamPrivate(Resource):
    method_decorators = [require_team_mode]

    @authed_only
    @require_team
    @teams_namespace.doc(
        description="Endpoint to get the current user's Team object",
        responses={
            200: ("Success", "TeamDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self):
        team = get_current_team()
        response = TeamSchema(view="self").dump(team)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        # A team can always calculate their score regardless of any setting because they can simply sum all of their challenges
        # Therefore a team requesting their private data should be able to get their own current score
        # However place is not something that a team can ascertain on their own so it is always gated behind freeze time
        response.data["place"] = team.place
        response.data["score"] = team.get_score(admin=True)
        return {"success": True, "data": response.data}

    @authed_only
    @require_team
    @teams_namespace.doc(
        description="Endpoint to edit the current user's Team object",
        responses={
            200: ("Success", "TeamDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self):
        team = get_current_team()
        if team.captain_id != session["id"]:
            return (
                {
                    "success": False,
                    "errors": {"": ["Only team captains can edit team information"]},
                },
                403,
            )

        data = request.get_json()

        response = TeamSchema(view="self", instance=team, partial=True).load(data)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()
        clear_team_session(team_id=team.id)
        response = TeamSchema("self").dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @authed_only
    @require_team
    @teams_namespace.doc(
        description="Endpoint to disband your current team. Can only be used if the team has performed no actions in the CTF.",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self):
        team_disbanding = get_config("team_disbanding", default="inactive_only")
        if team_disbanding == "disabled":
            return (
                {
                    "success": False,
                    "errors": {"": ["Team disbanding is currently disabled"]},
                },
                403,
            )

        team = get_current_team()
        if team.captain_id != session["id"]:
            return (
                {
                    "success": False,
                    "errors": {"": ["Only team captains can disband their team"]},
                },
                403,
            )

        # The team must not have performed any actions in the CTF
        performed_actions = any(
            [
                team.solves != [],
                team.fails != [],
                team.awards != [],
                Submissions.query.filter_by(team_id=team.id).all() != [],
                Unlocks.query.filter_by(team_id=team.id).all() != [],
            ]
        )

        if performed_actions:
            return (
                {
                    "success": False,
                    "errors": {
                        "": [
                            "You cannot disband your team as it has participated in the event. "
                            "Please contact an admin to disband your team or remove a member."
                        ]
                    },
                },
                403,
            )

        for member in team.members:
            member.team_id = None
            clear_user_session(user_id=member.id)

        db.session.delete(team)
        db.session.commit()

        clear_team_session(team_id=team.id)
        clear_standings()
        clear_challenges()

        db.session.close()

        return {"success": True}


@teams_namespace.route("/me/members")
class TeamPrivateMembers(Resource):
    method_decorators = [require_team_mode]

    @authed_only
    @require_team
    def post(self):
        team = get_current_team()
        if team.captain_id != session["id"]:
            return (
                {
                    "success": False,
                    "errors": {"": ["Only team captains can generate invite codes"]},
                },
                403,
            )

        invite_code = team.get_invite_code()
        response = {"code": invite_code}
        return {"success": True, "data": response}


@teams_namespace.route("/<team_id>/members")
@teams_namespace.param("team_id", "Team ID")
class TeamMembers(Resource):
    method_decorators = [require_team_mode]

    @admins_only
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        view = "admin" if is_admin() else "user"
        schema = TeamSchema(view=view)
        response = schema.dump(team)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        members = response.data.get("members")

        return {"success": True, "data": members}

    @admins_only
    def post(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        # Generate an invite code if no user or body is specified
        if len(request.data) == 0:
            invite_code = team.get_invite_code()
            response = {"code": invite_code}
            return {"success": True, "data": response}

        data = request.get_json()
        user_id = data.get("user_id")
        user = Users.query.filter_by(id=user_id).first_or_404()
        if user.team_id is None:
            team.members.append(user)
            db.session.commit()
        else:
            return (
                {
                    "success": False,
                    "errors": {"id": ["User has already joined a team"]},
                },
                400,
            )

        view = "admin" if is_admin() else "user"
        schema = TeamSchema(view=view)
        response = schema.dump(team)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        members = response.data.get("members")

        return {"success": True, "data": members}

    @admins_only
    def delete(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        data = request.get_json()
        user_id = data["user_id"]
        user = Users.query.filter_by(id=user_id).first_or_404()

        if user.team_id == team.id:
            team.members.remove(user)

            # Remove information that links the user to the team
            Submissions.query.filter_by(user_id=user.id).delete()
            Awards.query.filter_by(user_id=user.id).delete()
            Unlocks.query.filter_by(user_id=user.id).delete()

            db.session.commit()
        else:
            return (
                {"success": False, "errors": {"id": ["User is not part of this team"]}},
                400,
            )

        view = "admin" if is_admin() else "user"
        schema = TeamSchema(view=view)
        response = schema.dump(team)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        members = response.data.get("members")

        return {"success": True, "data": members}


@teams_namespace.route("/me/solves")
class TeamPrivateSolves(Resource):
    method_decorators = [require_team_mode]

    @authed_only
    @require_team
    def get(self):
        team = get_current_team()
        solves = team.get_solves(admin=True)

        view = "admin" if is_admin() else "user"
        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@teams_namespace.route("/me/fails")
class TeamPrivateFails(Resource):
    method_decorators = [require_team_mode]

    @authed_only
    @require_team
    def get(self):
        team = get_current_team()
        fails = team.get_fails(admin=True)

        view = "admin" if is_admin() else "user"

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            schema = SubmissionSchema(view=view, many=True)
            response = schema.dump(fails)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []
        count = len(fails)

        return {"success": True, "data": data, "meta": {"count": count}}


@teams_namespace.route("/me/awards")
class TeamPrivateAwards(Resource):
    method_decorators = [require_team_mode]

    @authed_only
    @require_team
    def get(self):
        team = get_current_team()
        awards = team.get_awards(admin=True)

        schema = AwardSchema(many=True)
        response = schema.dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@teams_namespace.route("/<team_id>/solves")
@teams_namespace.param("team_id", "Team ID")
class TeamPublicSolves(Resource):
    method_decorators = [require_team_mode]

    @check_account_visibility
    @check_score_visibility
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        if (team.banned or team.hidden) and is_admin() is False:
            abort(404)
        solves = team.get_solves(admin=is_admin())

        view = "admin" if is_admin() else "user"
        schema = SubmissionSchema(view=view, many=True)
        response = schema.dump(solves)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}


@teams_namespace.route("/<team_id>/fails")
@teams_namespace.param("team_id", "Team ID")
class TeamPublicFails(Resource):
    method_decorators = [require_team_mode]

    @check_account_visibility
    @check_score_visibility
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        if (team.banned or team.hidden) and is_admin() is False:
            abort(404)
        fails = team.get_fails(admin=is_admin())

        view = "admin" if is_admin() else "user"

        # We want to return the count purely for stats & graphs
        # but this data isn't really needed by the end user.
        # Only actually show fail data for admins.
        if is_admin():
            schema = SubmissionSchema(view=view, many=True)
            response = schema.dump(fails)

            if response.errors:
                return {"success": False, "errors": response.errors}, 400

            data = response.data
        else:
            data = []
        count = len(fails)

        return {"success": True, "data": data, "meta": {"count": count}}


@teams_namespace.route("/<team_id>/awards")
@teams_namespace.param("team_id", "Team ID")
class TeamPublicAwards(Resource):
    method_decorators = [require_team_mode]

    @check_account_visibility
    @check_score_visibility
    def get(self, team_id):
        team = Teams.query.filter_by(id=team_id).first_or_404()

        if (team.banned or team.hidden) and is_admin() is False:
            abort(404)
        awards = team.get_awards(admin=is_admin())

        schema = AwardSchema(many=True)
        response = schema.dump(awards)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        count = len(response.data)
        return {"success": True, "data": response.data, "meta": {"count": count}}
