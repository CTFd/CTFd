from sqlalchemy.sql.expression import union_all

from CTFd.models import db, Teams, Solves, Awards, Challenges
from CTFd.utils.dates import unix_time_to_utc
from CTFd.utils import config, get_config


def get_standings(*args, **kwargs):
    if config.user_mode() == 'teams':
        return get_team_standings(*args, **kwargs)
    elif config.user_mode() == 'users':
        return get_user_standings(*args, **kwargs)


def get_user_standings(admin=False, count=None):
    pass


def get_team_standings(admin=False, count=None):
    """
    Get team standings as a list of tuples containing team_id, team_name, and score e.g. [(team_id, team_name, score)].

    Ties are broken by who reached a given score first based on the solve ID. Two users can have the same score but one
    user will have a solve ID that is before the others. That user will be considered the tie-winner.

    Challenges & Awards with a value of zero are filtered out of the calculations to avoid incorrect tie breaks.
    """
    scores = db.session.query(
        Solves.team_id.label('team_id'),
        db.func.sum(Challenges.value).label('score'),
        db.func.max(Solves.id).label('id'),
        db.func.max(Solves.date).label('date')
    ).join(Challenges) \
        .filter(Challenges.value != 0) \
        .group_by(Solves.team_id)

    awards = db.session.query(
        Awards.team_id.label('team_id'),
        db.func.sum(Awards.value).label('score'),
        db.func.max(Awards.id).label('id'),
        db.func.max(Awards.date).label('date')
    ) \
        .filter(Awards.value != 0) \
        .group_by(Awards.team_id)

    """
    Filter out solves and awards that are before a specific time point.
    """
    freeze = get_config('freeze')
    if not admin and freeze:
        scores = scores.filter(Solves.date < unix_time_to_utc(freeze))
        awards = awards.filter(Awards.date < unix_time_to_utc(freeze))

    """
    Combine awards and solves with a union. They should have the same amount of columns
    """
    results = union_all(scores, awards).alias('results')

    """
    Sum each of the results by the team id to get their score.
    """
    sumscores = db.session.query(
        results.columns.team_id,
        db.func.sum(results.columns.score).label('score'),
        db.func.max(results.columns.id).label('id'),
        db.func.max(results.columns.date).label('date')
    ).group_by(results.columns.team_id) \
        .subquery()

    """
    Admins can see scores for all users but the public cannot see banned users.

    Filters out banned users.
    Properly resolves value ties by ID.

    Different databases treat time precision differently so resolve by the row ID instead.
    """
    if admin:
        standings_query = db.session.query(
            Teams.id.label('team_id'),
            Teams.name.label('name'),
            Teams.banned, sumscores.columns.score
        ) \
            .join(sumscores, Teams.id == sumscores.columns.team_id) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)
    else:
        standings_query = db.session.query(
            Teams.id.label('team_id'),
            Teams.name.label('name'),
            sumscores.columns.score
        ) \
            .join(sumscores, Teams.id == sumscores.columns.team_id) \
            .filter(Teams.banned == False) \
            .order_by(sumscores.columns.score.desc(), sumscores.columns.id)

    """
    Only select a certain amount of users if asked.
    """
    if count is None:
        standings = standings_query.all()
    else:
        standings = standings_query.limit(count).all()
    db.session.close()

    return standings
