from flask_restplus import Namespace, Resource
from CTFd.models import db, Challenges, Solves, Teams, Users
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils import config
from CTFd.utils.modes import TEAMS_MODE, USERS_MODE
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from CTFd.api.v1.statistics import statistics_namespace
from sqlalchemy import func
from sqlalchemy.sql import or_


@statistics_namespace.route('/challenges/<column>')
class ChallengePropertyCounts(Resource):
    @admins_only
    def get(self, column):
        if column in Challenges.__table__.columns.keys():
            prop = getattr(Challenges, column)
            data = Challenges.query\
                .with_entities(prop, func.count(prop))\
                .group_by(prop)\
                .all()
            return dict(data)
        else:
            response = {
                'message': 'That could not be found'
            }, 404
            return response


@statistics_namespace.route('/challenges/solves')
class ChallengeSolveStatistics(Resource):
    def get(self):
        chals = Challenges.query \
            .filter(or_(Challenges.hidden != True, Challenges.hidden == None)) \
            .order_by(Challenges.value) \
            .all()

        if config.user_mode() == TEAMS_MODE:
            solves_sub = db.session.query(
                Solves.challenge_id,
                db.func.count(Solves.challenge_id).label('solves')
            ) \
                .join(Teams, Solves.team_id == Teams.id) \
                .filter(Teams.banned == False) \
                .group_by(Solves.challenge_id).subquery()
        elif config.user_mode() == USERS_MODE:
            solves_sub = db.session.query(
                Solves.challenge_id,
                db.func.count(Solves.challenge_id).label('solves')
            ) \
                .join(Users, Solves.user_id == Users.id) \
                .filter(Users.banned == False) \
                .group_by(Solves.challenge_id).subquery()

        solves = db.session.query(
            solves_sub.columns.challenge_id,
            solves_sub.columns.solves,
            Challenges.name
        ) \
            .join(Challenges, solves_sub.columns.challenge_id == Challenges.id).all()

        response = {}
        if config.hide_scores():
            for chal, count, name in solves:
                response[chal] = -1
            for c in chals:
                if c.id not in response:
                    response[c.id] = -1
        else:
            for chal, count, name in solves:
                response[chal] = {
                    'name': name,
                    'solves': count,
                }
            for c in chals:
                if c.id not in response:
                    response[c.id] = {
                        'name': c.name,
                        'solves': 0,
                    }
        db.session.close()
        return response