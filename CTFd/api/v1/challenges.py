import math
from datetime import datetime, timedelta
from typing import List  # noqa: I001

from flask import abort, render_template, request, session, url_for
from flask_restx import Namespace, Resource
from sqlalchemy.sql import and_

from CTFd.api.v1.helpers.request import validate_args
from CTFd.api.v1.helpers.schemas import sqlalchemy_to_pydantic
from CTFd.api.v1.schemas import APIDetailedSuccessResponse, APIListSuccessResponse
from CTFd.cache import cache, clear_challenges, clear_ratings, clear_standings
from CTFd.constants import RawEnum
from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import ChallengeFiles as ChallengeFilesModel
from CTFd.models import Challenges
from CTFd.models import ChallengeTopics as ChallengeTopicsModel
from CTFd.models import (
    Fails,
    Flags,
    Hints,
    HintUnlocks,
    Ratings,
    Solves,
    Submissions,
    Tags,
    Tracking,
    db,
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.ratings import RatingSchema
from CTFd.schemas.tags import TagSchema
from CTFd.utils import config, get_config
from CTFd.utils import user as current_user
from CTFd.utils.challenges import (
    get_all_challenges,
    get_rating_average_for_challenge_id,
    get_solve_counts_for_challenges,
    get_solve_ids_for_user_id,
    get_solves_for_challenge_id,
)
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    scores_visible,
)
from CTFd.utils.dates import ctf_ended, ctf_paused, ctftime, isoformat
from CTFd.utils.decorators import (
    admins_only,
    authed_only,
    during_ctf_time_only,
    require_verified_emails,
)
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_challenge_visibility,
    check_score_visibility,
)
from CTFd.utils.humanize.words import pluralize
from CTFd.utils.logging import log
from CTFd.utils.security.signing import serialize
from CTFd.utils.user import (
    authed,
    get_current_team,
    get_current_team_attrs,
    get_current_user,
    get_current_user_attrs,
    get_ip,
    is_admin,
)

challenges_namespace = Namespace(
    "challenges", description="Endpoint to retrieve Challenges"
)

ChallengeModel = sqlalchemy_to_pydantic(
    Challenges, include={"solves": int, "solved_by_me": bool}
)
TransientChallengeModel = sqlalchemy_to_pydantic(Challenges, exclude=["id"])


class ChallengeDetailedSuccessResponse(APIDetailedSuccessResponse):
    data: ChallengeModel


class ChallengeListSuccessResponse(APIListSuccessResponse):
    data: List[ChallengeModel]


challenges_namespace.schema_model(
    "ChallengeDetailedSuccessResponse", ChallengeDetailedSuccessResponse.apidoc()
)

challenges_namespace.schema_model(
    "ChallengeListSuccessResponse", ChallengeListSuccessResponse.apidoc()
)


@challenges_namespace.route("")
class ChallengeList(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    @challenges_namespace.doc(
        description="Endpoint to get Challenge objects in bulk",
        responses={
            200: ("Success", "ChallengeListSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    @validate_args(
        {
            "name": (str, None),
            "max_attempts": (int, None),
            "value": (int, None),
            "category": (str, None),
            "type": (str, None),
            "state": (str, None),
            "q": (str, None),
            "field": (
                RawEnum(
                    "ChallengeFields",
                    {
                        "name": "name",
                        "description": "description",
                        "category": "category",
                        "type": "type",
                        "state": "state",
                    },
                ),
                None,
            ),
        },
        location="query",
    )
    def get(self, query_args):
        # Require a team if in teams mode
        # TODO: Convert this into a re-useable decorator
        # TODO: The require_team decorator doesnt work because of no admin passthru
        if get_current_user_attrs():
            if is_admin():
                pass
            else:
                if config.is_teams_mode() and get_current_team_attrs() is None:
                    abort(403)

        # Build filtering queries
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))

        # Admins get a shortcut to see all challenges despite pre-requisites
        admin_view = is_admin() and request.args.get("view") == "admin"

        # Get a cached mapping of challenge_id to solve_count
        solve_counts = get_solve_counts_for_challenges(admin=admin_view)

        # Get list of solve_ids for current user
        if authed():
            user = get_current_user()
            user_solves = get_solve_ids_for_user_id(user_id=user.id)
        else:
            user_solves = set()

        # Aggregate the query results into the hashes defined at the top of
        # this block for later use
        if scores_visible() and accounts_visible():
            solve_count_dfl = 0
        else:
            # Empty out the solves_count if we're hiding scores/accounts
            solve_counts = {}
            # This is necessary to match the challenge detail API which returns
            # `None` for the solve count if visiblity checks fail
            solve_count_dfl = None

        chal_q = get_all_challenges(admin=admin_view, field=field, q=q, **query_args)

        # Iterate through the list of challenges, adding to the object which
        # will be JSONified back to the client
        response = []
        tag_schema = TagSchema(view="user", many=True)

        # Gather all challenge IDs so that we can determine invalid challenge prereqs
        all_challenge_ids = {
            c.id for c in Challenges.query.with_entities(Challenges.id).all()
        }
        for challenge in chal_q:
            if challenge.requirements:
                requirements = challenge.requirements.get("prerequisites", [])
                anonymize = challenge.requirements.get("anonymize")
                prereqs = set(requirements).intersection(all_challenge_ids)
                if user_solves >= prereqs or admin_view:
                    pass
                else:
                    if anonymize:
                        response.append(
                            {
                                "id": challenge.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "solves": None,
                                "solved_by_me": False,
                                "category": "???",
                                "tags": [],
                                "template": "",
                                "script": "",
                            }
                        )
                    # Fallthrough to continue
                    continue

            try:
                challenge_type = get_chal_class(challenge.type)
            except KeyError:
                # Challenge type does not exist. Fall through to next challenge.
                continue

            # Challenge passes all checks, add it to response
            response.append(
                {
                    "id": challenge.id,
                    "type": challenge_type.name,
                    "name": challenge.name,
                    "value": challenge.value,
                    "solves": solve_counts.get(challenge.id, solve_count_dfl),
                    "solved_by_me": challenge.id in user_solves,
                    "category": challenge.category,
                    "tags": tag_schema.dump(challenge.tags).data,
                    "template": challenge_type.templates["view"],
                    "script": challenge_type.scripts["view"],
                }
            )

        db.session.close()
        return {"success": True, "data": response}

    @admins_only
    @challenges_namespace.doc(
        description="Endpoint to create a Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def post(self):
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_type = data.get("type", "standard")

        challenge_class = get_chal_class(challenge_type)
        try:
            challenge = challenge_class.create(request)
        except ChallengeCreateException as e:
            return {"success": False, "errors": {"": [str(e)]}}, 500

        response = challenge_class.read(challenge)

        clear_challenges()

        return {"success": True, "data": response}


@challenges_namespace.route("/types")
class ChallengeTypes(Resource):
    @admins_only
    def get(self):
        response = {}

        for class_id in CHALLENGE_CLASSES:
            challenge_class = CHALLENGE_CLASSES.get(class_id)
            response[challenge_class.id] = {
                "id": challenge_class.id,
                "name": challenge_class.name,
                "templates": challenge_class.templates,
                "scripts": challenge_class.scripts,
                "create": render_template(
                    challenge_class.templates["create"].lstrip("/")
                ),
            }
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>")
class Challenge(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    @challenges_namespace.doc(
        description="Endpoint to get a specific Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def get(self, challenge_id):
        if is_admin():
            chal = Challenges.query.filter(Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        if chal.requirements:
            requirements = chal.requirements.get("prerequisites", [])
            anonymize = chal.requirements.get("anonymize")
            # Gather all challenge IDs so that we can determine invalid challenge prereqs
            all_challenge_ids = {
                c.id for c in Challenges.query.with_entities(Challenges.id).all()
            }
            if challenges_visible():
                user = get_current_user()
                if user:
                    solve_ids = (
                        Solves.query.with_entities(Solves.challenge_id)
                        .filter_by(account_id=user.account_id)
                        .order_by(Solves.challenge_id.asc())
                        .all()
                    )
                else:
                    # We need to handle the case where a user is viewing challenges anonymously
                    solve_ids = []
                solve_ids = {value for value, in solve_ids}
                prereqs = set(requirements).intersection(all_challenge_ids)
                if solve_ids >= prereqs or is_admin():
                    pass
                else:
                    if anonymize:
                        return {
                            "success": True,
                            "data": {
                                "id": chal.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "logic": None,
                                "solves": None,
                                "solved_by_me": False,
                                "solution_id": None,
                                "category": "???",
                                "tags": [],
                                "template": "",
                                "script": "",
                            },
                        }
                    abort(403)
            else:
                abort(403)

        tags = [
            tag["value"] for tag in TagSchema("user", many=True).dump(chal.tags).data
        ]

        unlocked_hints = set()
        hints = []
        if authed():
            user = get_current_user()
            team = get_current_team()

            # TODO: Convert this into a re-useable decorator
            if is_admin():
                pass
            else:
                if config.is_teams_mode() and team is None:
                    abort(403)

            unlocked_hints = {
                u.target
                for u in HintUnlocks.query.filter_by(
                    type="hints", account_id=user.account_id
                )
            }
            files = []
            for f in chal.files:
                token = {
                    "user_id": user.id,
                    "team_id": team.id if team else None,
                    "file_id": f.id,
                }
                files.append(
                    url_for("views.files", path=f.location, token=serialize(token))
                )
        else:
            files = [url_for("views.files", path=f.location) for f in chal.files]

        for hint in Hints.query.filter_by(challenge_id=chal.id).all():
            if hint.id in unlocked_hints or ctf_ended():
                hints.append(
                    {
                        "id": hint.id,
                        "cost": hint.cost,
                        "title": hint.title,
                        "content": hint.content,
                    }
                )
            else:
                hints.append({"id": hint.id, "cost": hint.cost, "title": hint.title})

        response = chal_class.read(challenge=chal)

        # Get list of solve_ids for current user
        if authed():
            user = get_current_user()
            user_solves = get_solve_ids_for_user_id(user_id=user.id)
        else:
            user_solves = []

        solves_count = get_solve_counts_for_challenges(challenge_id=chal.id)
        if solves_count:
            challenge_id = chal.id
            solve_count = solves_count.get(chal.id)
            solved_by_user = challenge_id in user_solves
        else:
            solve_count, solved_by_user = 0, False

        # Hide solve counts if we are hiding solves/accounts
        if scores_visible() is False or accounts_visible() is False:
            solve_count = None

        if authed():
            # Get current attempts for the user
            attempts_query = Submissions.query.filter_by(
                account_id=user.account_id, challenge_id=challenge_id
            )
            max_attempts_behavior = get_config("max_attempts_behavior", "lockout")
            if max_attempts_behavior == "timeout":
                max_attempts_timeout = int(get_config("max_attempts_timeout", 300))
                timeout_delta = datetime.utcnow() - timedelta(
                    seconds=max_attempts_timeout
                )
                attempts_query = attempts_query.filter(
                    Submissions.date >= timeout_delta
                )
            attempts = attempts_query.count()
            rating = Ratings.query.filter_by(
                user_id=user.id, challenge_id=challenge_id
            ).first()
            if rating:
                rating = {
                    "value": rating.value,
                    "review": rating.review,
                }
        else:
            attempts = 0
            rating = None

        response["solves"] = solve_count
        response["solved_by_me"] = solved_by_user
        response["attempts"] = attempts
        response["files"] = files
        response["tags"] = tags
        response["hints"] = hints

        # If we didn't disable ratings then we should allow the user to see their own challenge rating
        if get_config("challenge_ratings", default="public") != "disabled":
            response["rating"] = rating
        else:
            response["rating"] = None
            rating = None

        # If ratings are public then we show the aggregated ratings
        if get_config("challenge_ratings", default="public") == "public":
            # Get rating information for this challenge
            rating_info = get_rating_average_for_challenge_id(challenge_id)
            response["ratings"] = {
                "up": rating_info.up,
                "down": rating_info.down,
                "count": rating_info.count,
            }
        else:
            rating_info = None
            response["ratings"] = None

        solution_id = None
        solution_state = "hidden"
        if chal.solution_id:
            # Share the solution state to the user but default to hidden
            solution_state = chal.solution.state
            # We explicitly want the solution visible
            if chal.solution.state == "visible":
                solution_id = chal.solution.id
            # We only want the solution to be visible if the challenge has been solved
            elif chal.solution.state == "solved":
                if int(challenge_id) in user_solves:
                    solution_id = chal.solution.id
        response["solution_id"] = solution_id
        response["solution_state"] = solution_state

        response["view"] = render_template(
            chal_class.templates["view"].lstrip("/"),
            solves=solve_count,
            solved_by_me=solved_by_user,
            files=files,
            tags=tags,
            hints=[Hints(**h) for h in hints],
            rating=rating,
            ratings=rating_info,
            max_attempts=chal.max_attempts,
            attempts=attempts,
            challenge=chal,
        )

        if (
            authed() is True
            and is_admin() is False
            and Tracking.query.filter_by(
                type="challenges.open", user_id=session["id"], target=challenge_id
            ).first()
            is None
        ):
            track = Tracking(
                ip=get_ip(),
                user_id=session["id"],
                type="challenges.open",
                target=challenge_id,
            )
            db.session.add(track)
            db.session.commit()
            db.session.close()

        return {"success": True, "data": response}

    @admins_only
    @challenges_namespace.doc(
        description="Endpoint to edit a specific Challenge object",
        responses={
            200: ("Success", "ChallengeDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
    )
    def patch(self, challenge_id):
        data = request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        challenge_class = get_chal_class(challenge.type)

        try:
            challenge = challenge_class.update(challenge, request)
        except ChallengeUpdateException as e:
            return {"success": False, "errors": {"": [str(e)]}}, 500

        response = challenge_class.read(challenge)

        clear_standings()
        clear_challenges()

        return {"success": True, "data": response}

    @admins_only
    @challenges_namespace.doc(
        description="Endpoint to delete a specific Challenge object",
        responses={200: ("Success", "APISimpleSuccessResponse")},
    )
    def delete(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(challenge.type)
        chal_class.delete(challenge)

        clear_standings()
        clear_challenges()

        return {"success": True}


@challenges_namespace.route("/attempt")
class ChallengeAttempt(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    def post(self):
        if authed() is False:
            return {"success": True, "data": {"status": "authentication_required"}}, 403

        if not request.is_json:
            request_data = request.form
        else:
            request_data = request.get_json()

        challenge_id = request_data.get("challenge_id")

        if current_user.is_admin():
            preview = request.args.get("preview", False)
            if preview:
                challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
                chal_class = get_chal_class(challenge.type)
                response = chal_class.attempt(challenge, request)
                # TODO: CTFd 4.0 We should remove the tuple strategy for Challenge plugins in favor of ChallengeResponse
                if isinstance(response, tuple):
                    status = "correct" if response[0] else "incorrect"
                    message = response[1]
                else:
                    status = response.status
                    message = response.message

                return {
                    "success": True,
                    "data": {
                        "status": status,
                        "message": message,
                    },
                }

        if ctf_paused():
            return (
                {
                    "success": True,
                    "data": {
                        "status": "paused",
                        "message": "{} is paused".format(config.ctf_name()),
                    },
                },
                403,
            )

        user = get_current_user()
        team = get_current_team()

        # TODO: Convert this into a re-useable decorator
        if config.is_teams_mode() and team is None:
            abort(403)

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        if challenge.state == "hidden":
            abort(404)

        if challenge.state == "locked":
            abort(403)

        if challenge.requirements:
            requirements = challenge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.challenge_id)
                .filter_by(account_id=user.account_id)
                .order_by(Solves.challenge_id.asc())
                .all()
            )
            solve_ids = {solve_id for solve_id, in solve_ids}
            # Gather all challenge IDs so that we can determine invalid challenge prereqs
            all_challenge_ids = {
                c.id for c in Challenges.query.with_entities(Challenges.id).all()
            }
            prereqs = set(requirements).intersection(all_challenge_ids)
            if solve_ids >= prereqs:
                pass
            else:
                abort(403)

        chal_class = get_chal_class(challenge.type)

        # Anti-bruteforce / submitting Flags too quickly
        kpm = current_user.get_wrong_submissions_per_minute(user.account_id)
        kpm_limit = int(get_config("incorrect_submissions_per_min", default=10))

        # Serialize attempt counting through redis to get a more accurate attempt count
        acc_kpm_key = f"account_kpm_{user.account_id}_{challenge.id}"
        recent_attempt_count = cache.inc(acc_kpm_key)
        cache.expire(acc_kpm_key, 60)

        if kpm > kpm_limit or recent_attempt_count > kpm_limit:
            if ctftime():
                chal_class.fail(
                    user=user, team=team, challenge=challenge, request=request
                )
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [TOO FAST]",
                name=user.name,
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
                kpm=kpm,
            )
            # Submitting too fast
            return (
                {
                    "success": True,
                    "data": {
                        "status": "ratelimited",
                        "message": "You're submitting flags too fast. Slow down.",
                    },
                },
                429,
            )

        solves = Solves.query.filter_by(
            account_id=user.account_id, challenge_id=challenge_id
        ).first()
        # We default fails to 0 as it's not needed unless we are working with max attempts
        fails = 0

        # Challenge not solved yet
        if not solves:
            # Hit max attempts
            max_tries = challenge.max_attempts
            if max_tries and max_tries > 0:
                max_attempts_behavior = get_config("max_attempts_behavior", "lockout")
                fails_query = Fails.query.filter_by(
                    account_id=user.account_id, challenge_id=challenge_id
                )
                if max_attempts_behavior == "timeout":  # Use timeout behavior
                    max_attempts_timeout = int(get_config("max_attempts_timeout", 300))
                    timeout_delta = datetime.utcnow() - timedelta(
                        seconds=max_attempts_timeout
                    )
                    fails = fails_query.filter(Fails.date >= timeout_delta).count()
                    # Calculate actual time remaining for the most recent fail
                    response = f"Not accepted. Try again in {math.ceil(max_attempts_timeout / 60)} minutes"
                    if fails > 0:
                        most_recent_fail = (
                            fails_query.filter(Fails.date >= timeout_delta)
                            .order_by(Fails.date.asc())
                            .first()
                        )
                        if most_recent_fail:
                            time_since_fail = (
                                datetime.utcnow() - most_recent_fail.date
                            ).total_seconds()
                            remaining_seconds = max_attempts_timeout - time_since_fail
                            remaining_minutes = math.ceil(remaining_seconds / 60)
                            response = f"Not accepted. Try again in {remaining_minutes} minutes"
                else:  # Use lockout behavior
                    fails = fails_query.count()
                    response = "Not accepted. You have 0 tries remaining"

                if fails >= max_tries or recent_attempt_count > max_tries:
                    return (
                        {
                            "success": True,
                            "data": {
                                "status": "ratelimited",
                                "message": response,
                            },
                        },
                        403,
                    )

            response = chal_class.attempt(challenge, request)
            # TODO: CTFd 4.0 We should remove the tuple strategy for Challenge plugins in favor of ChallengeResponse
            if isinstance(response, tuple):
                status = response[0]
                message = response[1]
            else:
                status = response.status
                message = response.message

            if status == "correct" or status is True:
                # The challenge plugin says the input is right
                if ctftime() or current_user.is_admin():
                    chal_class.solve(
                        user=user, team=team, challenge=challenge, request=request
                    )
                    clear_standings()
                    clear_challenges()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [CORRECT]",
                    name=user.name,
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )
                return {
                    "success": True,
                    "data": {"status": "correct", "message": message},
                }
            elif status == "partial":
                # The challenge plugin says that the input is a partial solve
                if ctftime() or current_user.is_admin():
                    chal_class.partial(
                        user=user, team=team, challenge=challenge, request=request
                    )
                    clear_standings()
                    clear_challenges()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [PARTIAL]",
                    name=user.name,
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )
                return {
                    "success": True,
                    "data": {"status": "partial", "message": message},
                }
            elif status == "incorrect" or status is False:
                # The challenge plugin says the input is wrong
                if ctftime() or current_user.is_admin():
                    chal_class.fail(
                        user=user, team=team, challenge=challenge, request=request
                    )
                    clear_standings()
                    clear_challenges()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [WRONG]",
                    name=user.name,
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )

                if max_tries:
                    # Off by one since fails has changed since it was gotten
                    attempts_left = max_tries - fails - 1
                    tries_str = pluralize(attempts_left, singular="try", plural="tries")
                    # Add a punctuation mark if there isn't one
                    if message[-1] not in "!().;?[]{}":
                        message = message + "."
                    message = "{} You have {} {} remaining.".format(
                        message, attempts_left, tries_str
                    )
                    if attempts_left == 0:
                        max_attempts_behavior = get_config(
                            "max_attempts_behavior", "lockout"
                        )
                        if max_attempts_behavior == "timeout":
                            max_attempts_timeout = int(
                                get_config("max_attempts_timeout", 300)
                            )
                            # Calculate actual time remaining based on the most recent fail
                            timeout_delta = datetime.utcnow() - timedelta(
                                seconds=max_attempts_timeout
                            )
                            most_recent_fail = (
                                Fails.query.filter_by(
                                    account_id=user.account_id,
                                    challenge_id=challenge_id,
                                )
                                .filter(Fails.date >= timeout_delta)
                                .order_by(Fails.date.asc())
                                .first()
                            )
                            if most_recent_fail:
                                time_since_fail = (
                                    datetime.utcnow() - most_recent_fail.date
                                ).total_seconds()
                                remaining_seconds = (
                                    max_attempts_timeout - time_since_fail
                                )
                                remaining_minutes = math.ceil(remaining_seconds / 60)
                                message += f" Try again in {remaining_minutes} minutes"
                            else:
                                message += f" Try again in {math.ceil(max_attempts_timeout / 60)} minutes"
                    return {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": message,
                        },
                    }
                else:
                    return {
                        "success": True,
                        "data": {"status": "incorrect", "message": message},
                    }

        # Challenge already solved
        else:
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [ALREADY SOLVED]",
                name=user.name,
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
                kpm=kpm,
            )
            response = chal_class.attempt(challenge, request)
            # TODO: CTFd 4.0 We should remove the tuple strategy for Challenge plugins in favor of ChallengeResponse
            if isinstance(response, tuple):
                status = response[0]
                message = response[1]
            else:
                status = response.status
                message = response.message
            return {
                "success": True,
                "data": {
                    "status": "already_solved",
                    "message": f"{message} but you already solved this",
                },
            }


@challenges_namespace.route("/<challenge_id>/solves")
class ChallengeSolves(Resource):
    @check_challenge_visibility
    @check_account_visibility
    @check_score_visibility
    @during_ctf_time_only
    @require_verified_emails
    def get(self, challenge_id):
        response = []
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        # TODO: Need a generic challenge visibility call.
        # However, it should be stated that a solve on a gated challenge is not considered private.
        if challenge.state == "hidden" and is_admin() is False:
            abort(404)

        freeze = get_config("freeze")
        if freeze:
            preview = request.args.get("preview")
            if (is_admin() is False) or (is_admin() is True and preview):
                freeze = True
            elif is_admin() is True:
                freeze = False

        response = get_solves_for_challenge_id(challenge_id=challenge_id, freeze=freeze)

        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/files")
class ChallengeFiles(Resource):
    @admins_only
    def get(self, challenge_id):
        response = []

        challenge_files = ChallengeFilesModel.query.filter_by(
            challenge_id=challenge_id
        ).all()

        for f in challenge_files:
            response.append(
                {
                    "id": f.id,
                    "type": f.type,
                    "location": f.location,
                    "sha1sum": f.sha1sum,
                }
            )
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/tags")
class ChallengeTags(Resource):
    @admins_only
    def get(self, challenge_id):
        response = []

        tags = Tags.query.filter_by(challenge_id=challenge_id).all()

        for t in tags:
            response.append(
                {"id": t.id, "challenge_id": t.challenge_id, "value": t.value}
            )
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/topics")
class ChallengeTopics(Resource):
    @admins_only
    def get(self, challenge_id):
        response = []

        topics = ChallengeTopicsModel.query.filter_by(challenge_id=challenge_id).all()

        for t in topics:
            response.append(
                {
                    "id": t.id,
                    "challenge_id": t.challenge_id,
                    "topic_id": t.topic_id,
                    "value": t.topic.value,
                }
            )
        return {"success": True, "data": response}


@challenges_namespace.route("/<challenge_id>/hints")
class ChallengeHints(Resource):
    @admins_only
    def get(self, challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)
        response = schema.dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/flags")
class ChallengeFlags(Resource):
    @admins_only
    def get(self, challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}


@challenges_namespace.route("/<challenge_id>/requirements")
class ChallengeRequirements(Resource):
    @admins_only
    def get(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        return {"success": True, "data": challenge.requirements}


@challenges_namespace.route("/<challenge_id>/ratings")
class ChallengeRatings(Resource):
    @admins_only
    def get(self, challenge_id):
        """Get paginated ratings for a challenge"""
        # Get pagination parameters
        page = int(request.args.get("page", 1))

        # Get paginated ratings with user information
        ratings_query = Ratings.query.filter(
            Ratings.challenge_id == challenge_id
        ).order_by(Ratings.id.desc())

        paginated_ratings = ratings_query.paginate(
            page=page, max_per_page=50, error_out=False
        )

        # Use schema to serialize the ratings data
        schema = RatingSchema(view="admin", many=True)
        ratings_data = schema.dump(paginated_ratings.items)

        if ratings_data.errors:
            return {"success": False, "errors": ratings_data.errors}, 400

        # Use cached utility function to get rating statistics for meta
        rating_info = get_rating_average_for_challenge_id(challenge_id)

        return {
            "meta": {
                "pagination": {
                    "page": paginated_ratings.page,
                    "next": paginated_ratings.next_num,
                    "prev": paginated_ratings.prev_num,
                    "pages": paginated_ratings.pages,
                    "per_page": paginated_ratings.per_page,
                    "total": paginated_ratings.total,
                },
                "summary": {
                    "up": rating_info.up,
                    "down": rating_info.down,
                    "count": rating_info.count,
                },
            },
            "success": True,
            "data": ratings_data.data,
        }

    @check_challenge_visibility
    @during_ctf_time_only
    @authed_only
    @require_verified_emails
    def put(self, challenge_id):
        """Create or update a rating for a challenge"""
        # If challenge ratings are disabled we should not receive any ratings information
        # If they are public or private we still want to collect the data
        if get_config("challenge_ratings") == "disabled":
            abort(403)

        user = get_current_user()
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        # Check if challenge is visible to the user
        if challenge.state == "hidden" and not is_admin():
            abort(404)

        # Check if user/team has solved this challenge (only allow rating if solved)
        if not is_admin():
            user_solves = get_solve_ids_for_user_id(user_id=user.id)
            if int(challenge_id) not in user_solves:
                return {
                    "success": False,
                    "errors": {"": ["You must solve this challenge before rating it"]},
                }, 403

        data = request.get_json()
        if not data or "value" not in data:
            return {
                "success": False,
                "errors": {"value": ["Rating value is required"]},
            }, 400

        try:
            rating_value = int(data["value"])
        except (ValueError, TypeError):
            return {
                "success": False,
                "errors": {"value": ["Rating value must be an integer"]},
            }, 400

        # Validate rating value (1-5 scale)
        if abs(rating_value) != 1:
            return {
                "success": False,
                "errors": {"value": ["Rating value must be either 1 or -1"]},
            }, 400

        # Get review text (optional)
        review_text = data.get("review", "")
        if review_text and len(review_text) > 2000:
            return {
                "success": False,
                "errors": {"review": ["Review text cannot exceed 2000 characters"]},
            }, 400

        # Find existing rating or create new one
        rating = Ratings.query.filter_by(
            user_id=user.id, challenge_id=challenge_id
        ).first()

        if rating:
            # Update existing rating
            rating.value = rating_value
            rating.review = review_text
            rating.date = datetime.utcnow()
        else:
            # Create new rating
            rating = Ratings(
                user_id=user.id,
                challenge_id=challenge_id,
                value=rating_value,
                review=review_text,
            )
            db.session.add(rating)

        db.session.commit()

        # Clear cached rating data since we just created/updated a rating
        clear_ratings()

        return {
            "success": True,
            "data": {
                "id": rating.id,
                "user_id": rating.user_id,
                "challenge_id": rating.challenge_id,
                "value": rating.value,
                "review": rating.review,
                "date": isoformat(rating.date),
            },
        }


@challenges_namespace.route("/<challenge_id>/solution")
class ChallengeSolution(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @authed_only
    @require_verified_emails
    def get(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        # Check if challenge is visible to the user
        if challenge.state == "hidden" and not is_admin():
            abort(404)

        # Get user's current solves
        user = get_current_user_attrs()
        user_solves = get_solve_ids_for_user_id(user_id=user.id)

        response = {
            "id": None,
            "state": None,
        }
        solution_id = None
        solution_state = "hidden"
        if challenge.solution_id:
            # Share the solution state to the user but default to hidden
            solution_state = challenge.solution.state
            # We explicitly want the solution visible
            if challenge.solution.state == "visible":
                solution_id = challenge.solution.id
            # We only want the solution to be visible if the challenge has been solved
            elif challenge.solution.state == "solved":
                if int(challenge_id) in user_solves:
                    solution_id = challenge.solution.id
        response["id"] = solution_id
        response["state"] = solution_state
        return {"success": True, "data": response}
