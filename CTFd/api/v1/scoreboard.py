from collections import defaultdict

from flask import request
from flask_restx import Namespace, Resource
from sqlalchemy import select

from CTFd.cache import cache, make_cache_key
from CTFd.models import Brackets, Users, db
from CTFd.utils import get_config
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.modes import TEAMS_MODE, generate_account_url, get_mode_as_word
from CTFd.utils.scoreboard import get_scoreboard_detail
from CTFd.utils.scores import get_standings, get_user_standings

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
            r = db.session.execute(
                select(
                    [
                        Users.id,
                        Users.name,
                        Users.oauth_id,
                        Users.team_id,
                        Users.hidden,
                        Users.banned,
                        Users.bracket_id,
                        Brackets.name.label("bracket_name"),
                    ]
                )
                .where(Users.team_id.isnot(None))
                .join(Brackets, Users.bracket_id == Brackets.id, isouter=True)
            )
            users = r.fetchall()
            membership = defaultdict(dict)
            for u in users:
                if u.hidden is False and u.banned is False:
                    membership[u.team_id][u.id] = {
                        "id": u.id,
                        "oauth_id": u.oauth_id,
                        "name": u.name,
                        "score": 0,
                        "bracket_id": u.bracket_id,
                        "bracket_name": u.bracket_name,
                    }

            # Get user_standings as a dict so that we can more quickly get member scores
            user_standings = get_user_standings()
            for u in user_standings:
                membership[u.team_id][u.user_id]["score"] = int(u.score)

        for i, x in enumerate(standings):
            entry = {
                "pos": i + 1,
                "account_id": x.account_id,
                "account_url": generate_account_url(account_id=x.account_id),
                "account_type": account_type,
                "oauth_id": x.oauth_id,
                "name": x.name,
                "score": int(x.score),
                "bracket_id": x.bracket_id,
                "bracket_name": x.bracket_name,
            }

            if mode == TEAMS_MODE:
                entry["members"] = list(membership[x.account_id].values())

            response.append(entry)
        return {"success": True, "data": response}


@scoreboard_namespace.route("/top/<int:count>")
@scoreboard_namespace.param("count", "How many top teams to return")
class ScoreboardDetail(Resource):
    @check_account_visibility
    @check_score_visibility
    def get(self, count):
        # Restrict count to some limit
        count = max(1, min(count, 50))
        bracket_id = request.args.get("bracket_id")
        response = get_scoreboard_detail(count=count, bracket_id=bracket_id)
        return {"success": True, "data": response}
