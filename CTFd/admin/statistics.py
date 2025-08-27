from flask import render_template

from CTFd.admin import admin
from CTFd.models import Challenges, Fails, Solves, Teams, Tracking, Users, db
from CTFd.utils.config import get_config
from CTFd.utils.decorators import admins_only
from CTFd.utils.modes import get_model
from CTFd.utils.scores import get_standings
from CTFd.utils.updates import update_check


@admin.route("/admin/statistics", methods=["GET"])
@admins_only
def statistics():
    update_check()

    Model = get_model()

    teams_registered = Teams.query.count()
    users_registered = Users.query.count()

    wrong_count = (
        Fails.query.join(Model, Fails.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .count()
    )

    solve_count = (
        Solves.query.join(Model, Solves.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .count()
    )

    challenge_count = Challenges.query.count()

    total_points = (
        Challenges.query.with_entities(db.func.sum(Challenges.value).label("sum"))
        .filter_by(state="visible")
        .first()
        .sum
    ) or 0

    ip_count = Tracking.query.with_entities(Tracking.ip).distinct().count()

    solves_sub = (
        db.session.query(
            Solves.challenge_id, db.func.count(Solves.challenge_id).label("solves_cnt")
        )
        .join(Model, Solves.account_id == Model.id)
        .filter(Model.banned == False, Model.hidden == False)
        .group_by(Solves.challenge_id)
        .subquery()
    )

    solves = (
        db.session.query(
            solves_sub.columns.challenge_id,
            solves_sub.columns.solves_cnt,
            Challenges.name,
        )
        .join(Challenges, solves_sub.columns.challenge_id == Challenges.id)
        .all()
    )

    solve_data = {}
    for _chal, count, name in solves:
        solve_data[name] = count

    most_solved = None
    least_solved = None
    if len(solve_data):
        most_solved = max(solve_data, key=solve_data.get)
        least_solved = min(solve_data, key=solve_data.get)

    account_scores = get_standings(count=100, admin=True)

    # Get all challenges ordered by category and value
    all_challenges = (
        Challenges.query.filter(Challenges.state == "visible")
        .order_by(Challenges.value.asc(), Challenges.category)
        .all()
    )

    # Get solve matrix data for top 100 accounts
    top_account_ids = [account.account_id for account in account_scores]

    if top_account_ids:
        solve_matrix_data = (
            db.session.query(
                Solves.account_id,
                Solves.challenge_id,
                Challenges.name.label("challenge_name"),
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

        # Get attempt matrix data (fails) for top 100 accounts
        attempt_matrix_data = (
            db.session.query(
                Fails.account_id,
                Fails.challenge_id,
                Challenges.name.label("challenge_name"),
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

        # Get challenge opens matrix data for top 100 accounts
        # Need to handle mapping from user_id (in Tracking) to account_id (user or team)
        if get_config("user_mode") == "teams":
            # In teams mode, map user_id to team_id (account_id)
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
                    Tracking.target.isnot(None),  # Ensure target is not null
                    Tracking.type == "challenges.open",  # Only track challenge opens
                )
                .distinct()  # Remove duplicates if user opened same challenge multiple times
                .all()
            )
        else:
            # In users mode, user_id maps directly to account_id
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
                    Tracking.target.isnot(None),  # Ensure target is not null
                    Tracking.type == "challenges.open",  # Only track challenge opens
                )
                .distinct()  # Remove duplicates if user opened same challenge multiple times
                .all()
            )

        # Build matrix data structure
        account_solves = {}
        for account in account_scores:
            account_solves[account.account_id] = {
                "name": account.name,
                "score": account.score,
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
    else:
        account_solves = {}

    db.session.close()

    return render_template(
        "admin/statistics.html",
        user_count=users_registered,
        team_count=teams_registered,
        ip_count=ip_count,
        wrong_count=wrong_count,
        solve_count=solve_count,
        challenge_count=challenge_count,
        total_points=total_points,
        solve_data=solve_data,
        most_solved=most_solved,
        least_solved=least_solved,
        top_users=account_scores,
        all_challenges=all_challenges,
        account_solves=account_solves,
    )
