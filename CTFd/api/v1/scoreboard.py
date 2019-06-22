from flask_restplus import Namespace, Resource

from CTFd.models import Solves, Awards, Teams
from CTFd.cache import cache, make_cache_key
from CTFd.utils.scores import get_standings
from CTFd.utils import get_config
from CTFd.utils.modes import generate_account_url, get_mode_as_word, TEAMS_MODE
from CTFd.utils.dates import unix_time_to_utc, isoformat
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)

scoreboard_namespace = Namespace(
    "scoreboard", description="Endpoint to retrieve scores"
)


@scoreboard_namespace.route("")
class ScoreboardList(Resource):
    @check_account_visibility
    @check_score_visibility
    @cache.cached(timeout=60, key_prefix=make_cache_key)
    def get(self):
        standings = get_standings()
        response = []
        mode = get_config("user_mode")
        account_type = get_mode_as_word()

        if mode == TEAMS_MODE:
            team_ids = []
            for team in standings:
                team_ids.append(team.account_id)
            teams = Teams.query.filter(Teams.id.in_(team_ids)).all()
            teams = [next(t for t in teams if t.id == id) for id in team_ids]

        for i, x in enumerate(standings):
            entry = {
                "pos": i + 1,
                "account_id": x.account_id,
                "account_url": generate_account_url(account_id=x.account_id),
                "account_type": account_type,
                "oauth_id": x.oauth_id,
                "name": x.name,
                "score": int(x.score),
            }

            if mode == TEAMS_MODE:
                members = []
                for member in teams[i].members:
                    members.append(
                        {
                            "id": member.id,
                            "oauth_id": member.oauth_id,
                            "name": member.name,
                            "score": int(member.score),
                        }
                    )

                entry["members"] = members

            response.append(entry)
        return {"success": True, "data": response}


@scoreboard_namespace.route("/top/<count>")
@scoreboard_namespace.param("count", "How many top teams to return")
class ScoreboardDetail(Resource):
    @check_account_visibility
    @check_score_visibility
    @cache.cached(timeout=60, key_prefix=make_cache_key)
    def get(self, count):
        response = {}

        standings = get_standings(count=count)

        team_ids = [team.account_id for team in standings]

        solves = Solves.query.filter(Solves.account_id.in_(team_ids))
        awards = Awards.query.filter(Awards.account_id.in_(team_ids))

        freeze = get_config("freeze")

        if freeze:
            solves = solves.filter(Solves.date < unix_time_to_utc(freeze))
            awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

        solves = solves.all()
        awards = awards.all()

        for i, team in enumerate(team_ids):
            response[i + 1] = {
                "id": standings[i].account_id,
                "name": standings[i].name,
                "solves": [],
            }
            for solve in solves:
                if solve.account_id == team:
                    response[i + 1]["solves"].append(
                        {
                            "challenge_id": solve.challenge_id,
                            "account_id": solve.account_id,
                            "team_id": solve.team_id,
                            "user_id": solve.user_id,
                            "value": solve.challenge.value,
                            "date": isoformat(solve.date),
                        }
                    )
            for award in awards:
                if award.account_id == team:
                    response[i + 1]["solves"].append(
                        {
                            "challenge_id": None,
                            "account_id": award.account_id,
                            "team_id": award.team_id,
                            "user_id": award.user_id,
                            "value": award.value,
                            "date": isoformat(award.date),
                        }
                    )
            response[i + 1]["solves"] = sorted(
                response[i + 1]["solves"], key=lambda k: k["date"]
            )

        return {"success": True, "data": response}
