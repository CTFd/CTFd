from collections import defaultdict

from CTFd.cache import cache
from CTFd.models import Awards, Solves
from CTFd.utils import get_config
from CTFd.utils.dates import isoformat, unix_time_to_utc
from CTFd.utils.modes import generate_account_url
from CTFd.utils.scores import get_standings


@cache.memoize(timeout=60)
def get_scoreboard_detail(count, bracket_id=None):
    response = {}

    standings = get_standings(count=count, bracket_id=bracket_id)

    team_ids = [team.account_id for team in standings]

    solves = Solves.query.filter(Solves.account_id.in_(team_ids))
    awards = Awards.query.filter(Awards.account_id.in_(team_ids))

    freeze = get_config("freeze")

    if freeze:
        solves = solves.filter(Solves.date < unix_time_to_utc(freeze))
        awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

    solves = solves.all()
    awards = awards.all()

    # Build a mapping of accounts to their solves and awards
    solves_mapper = defaultdict(list)
    for solve in solves:
        solves_mapper[solve.account_id].append(
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
        solves_mapper[award.account_id].append(
            {
                "challenge_id": None,
                "account_id": award.account_id,
                "team_id": award.team_id,
                "user_id": award.user_id,
                "value": award.value,
                "date": isoformat(award.date),
            }
        )

    # Sort all solves by date
    for team_id in solves_mapper:
        solves_mapper[team_id] = sorted(solves_mapper[team_id], key=lambda k: k["date"])

    for i, x in enumerate(standings):
        response[i + 1] = {
            "id": x.account_id,
            "account_url": generate_account_url(account_id=x.account_id),
            "name": x.name,
            "score": int(x.score),
            "bracket_id": x.bracket_id,
            "bracket_name": x.bracket_name,
            "solves": solves_mapper.get(x.account_id, []),
        }

    return response
