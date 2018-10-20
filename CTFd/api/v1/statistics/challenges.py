from flask_restplus import Namespace, Resource
from CTFd.models import db, Challenges, Solves, Teams, Users
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils import config
from CTFd.utils.modes import get_model
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

        Model = get_model()

        solves_sub = db.session.query(
            Solves.challenge_id,
            db.func.count(Solves.challenge_id).label('solves')
        ) \
            .join(Model, Solves.account_id == Model.id) \
            .filter(Model.banned == False, Model.hidden == False) \
            .group_by(Solves.challenge_id).subquery()

        solves = db.session.query(
            solves_sub.columns.challenge_id,
            solves_sub.columns.solves,
            Challenges.name
        ) \
            .join(Challenges, solves_sub.columns.challenge_id == Challenges.id).all()

        response = []
        if config.hide_scores():
            # for chal, count, name in solves:
            #     response[chal] = -1
            # for c in chals:
            #     if c.id not in response:
            #         response[c.id] = -1
            return response
        else:
            has_solves = []
            for challenge_id, count, name in solves:
                challenge = {
                    'id': challenge_id,
                    'name': name,
                    'solves': count,
                }
                response.append(challenge)
                has_solves.append(challenge_id)
            for c in chals:
                if c.id not in has_solves:
                    challenge = {
                        'id': c.id,
                        'name': c.name,
                        'solves': 0,
                    }
                    response.append(challenge)
        db.session.close()
        return response


@statistics_namespace.route('/challenges/solves/percentages')
class ChallengeSolvePercentages(Resource):
    @admins_only
    def get(self):
        challenges = Challenges.query\
            .add_columns('id', 'name', 'hidden', 'max_attempts')\
            .order_by(Challenges.value).all()

        Model = get_model()

        teams_with_points = db.session.query(Solves.account_id) \
            .join(Model) \
            .filter(Model.banned == False) \
            .group_by(Solves.account_id) \
            .count()

        percentage_data = []
        for challenge in challenges:
            solve_count = Solves.query.join(Model, Solves.account_id == Model.id) \
                .filter(Solves.challenge_id == challenge.id, Model.banned == False, Model.hidden == False) \
                .count()

            if teams_with_points > 0:
                percentage = (float(solve_count) / float(teams_with_points))
            else:
                percentage = 0.0

            percentage_data.append({
                'id': challenge.id,
                'name': challenge.name,
                'percentage': percentage,
            })

        response = sorted(percentage_data, key=lambda x: x['percentage'], reverse=True)
        return response