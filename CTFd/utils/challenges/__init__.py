import datetime

from sqlalchemy import func as sa_func
from sqlalchemy.sql import and_, false, true

from CTFd.cache import cache
from CTFd.models import Solves, Users, db
from CTFd.utils import get_config
from CTFd.utils.dates import isoformat, unix_time_to_utc
from CTFd.utils.modes import generate_account_url, get_model


@cache.memoize(timeout=60)
def get_solves_for_challenge_id(challenge_id, freeze=False):
    Model = get_model()
    solves = (
        Solves.query.add_columns(Model.name.label("account_name"))
        .join(Model, Solves.account_id == Model.id)
        .filter(
            Solves.challenge_id == challenge_id,
            Model.banned == False,
            Model.hidden == False,
        )
        .order_by(Solves.date.asc())
    )
    if freeze:
        freeze_time = get_config("freeze")
        if freeze_time:
            dt = datetime.datetime.utcfromtimestamp(freeze_time)
            solves = solves.filter(Solves.date < dt)
    results = []

    for solve in solves:
        # Seperate out the account name and the Solve object from the SQLAlchemy tuple
        solve, account_name = solve
        results.append(
            {
                "account_id": solve.account_id,
                "name": account_name,
                "date": isoformat(solve.date),
                "account_url": generate_account_url(account_id=solve.account_id),
            }
        )
    return results


@cache.memoize(timeout=60)
def get_solve_ids_for_user_id(user_id):
    user = Users.query.filter_by(id=user_id).first()
    solve_ids = (
        Solves.query.with_entities(Solves.challenge_id)
        .filter(Solves.account_id == user.account_id)
        .all()
    )
    solve_ids = {value for value, in solve_ids}
    return solve_ids


@cache.memoize(timeout=60)
def get_solve_counts_for_challenges(challenge_id=None, admin=False):
    if challenge_id is None:
        challenge_id_filter = ()
    else:
        challenge_id_filter = (Solves.challenge_id == challenge_id,)
    AccountModel = get_model()
    freeze = get_config("freeze")
    if freeze and not admin:
        freeze_cond = Solves.date < unix_time_to_utc(freeze)
    else:
        freeze_cond = true()
    exclude_solves_cond = and_(
        AccountModel.banned == false(), AccountModel.hidden == false(),
    )
    solves_q = (
        db.session.query(Solves.challenge_id, sa_func.count(Solves.challenge_id),)
        .join(AccountModel)
        .filter(*challenge_id_filter, freeze_cond, exclude_solves_cond)
        .group_by(Solves.challenge_id)
    )

    solve_counts = {}
    for chal_id, solve_count in solves_q:
        solve_counts[chal_id] = solve_count
    return solve_counts
