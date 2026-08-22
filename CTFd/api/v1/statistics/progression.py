from flask import url_for
from flask_restx import Resource

from CTFd.api.v1.statistics import statistics_namespace
from CTFd.models import Brackets, Challenges, Fails, Solves, Teams, Tracking, Users, db
from CTFd.utils.config import get_config
from CTFd.utils.decorators import admins_only
from CTFd.utils.modes import get_model
from CTFd.utils.scores import get_standings


@statistics_namespace.route("/progression/matrix")
class ProgressionMatrix(Resource):
    @admins_only
    def get(self):
        Model = get_model()
        user_mode = get_config("user_mode")

        account_scores = get_standings(count=100, admin=True)

        # Get all visible challenges ordered by position, value, category
        all_challenges = (
            Challenges.query.filter(Challenges.state == "visible")
            .order_by(
                (
                    Challenges.position == 0
                ).asc(),  # Position of 0 should go to the end/bottom
                Challenges.position.asc(),  # Ordered challenges should go first
                Challenges.value,
                Challenges.category,
            )
            .all()
        )

        top_account_ids = [account.account_id for account in account_scores]

        account_solves = {}
        if top_account_ids:
            solve_matrix_data = (
                db.session.query(
                    Solves.account_id,
                    Solves.challenge_id,
                )
                .join(Challenges, Challenges.id == Solves.challenge_id)
                .join(Model, Model.id == Solves.account_id)
                .filter(
                    Solves.account_id.in_(top_account_ids),
                    Model.banned == False,
                    Model.hidden == False,
                    Challenges.state == "visible",
                )
                .all()
            )

            attempt_matrix_data = (
                db.session.query(
                    Fails.account_id,
                    Fails.challenge_id,
                )
                .join(Challenges, Challenges.id == Fails.challenge_id)
                .join(Model, Model.id == Fails.account_id)
                .filter(
                    Fails.account_id.in_(top_account_ids),
                    Model.banned == False,
                    Model.hidden == False,
                    Challenges.state == "visible",
                )
                .all()
            )

            if user_mode == "teams":
                opens_matrix_data = (
                    db.session.query(
                        Teams.id.label("account_id"),
                        Tracking.target.label("challenge_id"),
                    )
                    .join(Users, Users.id == Tracking.user_id)
                    .join(Teams, Teams.id == Users.team_id)
                    .join(Challenges, Challenges.id == Tracking.target)
                    .filter(
                        Teams.id.in_(top_account_ids),
                        Users.banned == False,
                        Users.hidden == False,
                        Teams.banned == False,
                        Teams.hidden == False,
                        Challenges.state == "visible",
                        Tracking.target.isnot(None),
                        Tracking.type == "challenges.open",
                    )
                    .distinct()
                    .all()
                )
            else:
                opens_matrix_data = (
                    db.session.query(
                        Tracking.user_id.label("account_id"),
                        Tracking.target.label("challenge_id"),
                    )
                    .join(Users, Users.id == Tracking.user_id)
                    .join(Challenges, Challenges.id == Tracking.target)
                    .filter(
                        Tracking.user_id.in_(top_account_ids),
                        Users.banned == False,
                        Users.hidden == False,
                        Challenges.state == "visible",
                        Tracking.target.isnot(None),
                        Tracking.type == "challenges.open",
                    )
                    .distinct()
                    .all()
                )

            for account in account_scores:
                account_solves[account.account_id] = {
                    "solved_challenges": set(),
                    "attempted_challenges": set(),
                    "opened_challenges": set(),
                }

            for solve in solve_matrix_data:
                if solve.account_id in account_solves:
                    account_solves[solve.account_id]["solved_challenges"].add(
                        solve.challenge_id
                    )

            for attempt in attempt_matrix_data:
                if attempt.account_id in account_solves:
                    account_solves[attempt.account_id]["attempted_challenges"].add(
                        attempt.challenge_id
                    )

            for opens in opens_matrix_data:
                if opens.account_id in account_solves:
                    account_solves[opens.account_id]["opened_challenges"].add(
                        opens.challenge_id
                    )

        # Build scoreboard data
        scoreboard_data = []
        for idx, user in enumerate(account_scores, start=1):
            if user_mode == "teams":
                account_url = url_for("admin.teams_detail", team_id=user.account_id)
            else:
                account_url = url_for("admin.users_detail", user_id=user.account_id)

            entry = {
                "id": user.account_id,
                "name": user.name,
                "score": int(user.score),
                "place": idx,
                "url": account_url,
                "bracket_id": user.bracket_id,
                "bracket_name": user.bracket_name,
                "solves": list(
                    account_solves.get(user.account_id, {}).get("solved_challenges", [])
                ),
                "attempts": list(
                    account_solves.get(user.account_id, {}).get(
                        "attempted_challenges", []
                    )
                ),
                "opens": list(
                    account_solves.get(user.account_id, {}).get("opened_challenges", [])
                ),
            }
            scoreboard_data.append(entry)

        # Build challenges data
        challenges_data = []
        for challenge in all_challenges:
            challenges_data.append(
                {
                    "id": challenge.id,
                    "name": challenge.name,
                    "value": challenge.value,
                    "position": challenge.position,
                    "category": challenge.category,
                    "url": url_for(
                        "admin.challenges_detail", challenge_id=challenge.id
                    ),
                }
            )

        # Build brackets data
        brackets_data = [
            {
                "id": bracket.id,
                "name": bracket.name,
                "description": bracket.description,
                "type": bracket.type,
            }
            for bracket in Brackets.query.all()
        ]

        db.session.close()

        return {
            "success": True,
            "data": {
                "scoreboard": scoreboard_data,
                "challenges": challenges_data,
                "brackets": brackets_data,
            },
        }
