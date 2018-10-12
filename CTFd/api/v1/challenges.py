from flask import session, request
from flask_restplus import Namespace, Resource
from CTFd.models import (
    db,
    Challenges,
    Unlocks,
    Tags,
    Hints,
    Flags,
    Solves,
    Teams,
    ChallengeFiles as ChallengeFilesModel,
)
from CTFd.plugins.challenges import get_chal_class, CHALLENGE_CLASSES
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    admins_only
)
from CTFd.schemas.tags import TagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.flags import FlagSchema
from sqlalchemy.sql import or_

challenges_namespace = Namespace('challenges', description="Endpoint to retrieve Challenges")


@challenges_namespace.route('')
class ChallengeList(Resource):
    @during_ctf_time_only
    @require_verified_emails
    @viewable_without_authentication(status_code=403)
    def get(self):
        challenges = Challenges.query.filter(
            or_(Challenges.hidden != True, Challenges.hidden == None)
        ).order_by(Challenges.value).all()

        response = []
        tag_schema = TagSchema(view='user', many=True)
        for challenge in challenges:
            challenge_type = get_chal_class(challenge.type)
            response.append({
                'id': challenge.id,
                'type': challenge_type.name,
                'name': challenge.name,
                'value': challenge.value,
                'category': challenge.category,
                'tags': tag_schema.dump(challenge.tags).data,
                'template': challenge_type.templates['modal'],
                'script': challenge_type.scripts['modal'],
            })

        db.session.close()
        return response

    @admins_only
    def post(self):
        challenge_type = request.form['type']
        challenge_class = get_chal_class(challenge_type)
        challenge = challenge_class.create(request)
        response = challenge_class.read(challenge)
        return response


@challenges_namespace.route('/types')
class ChallengeTypes(Resource):
    @admins_only
    def get(self):
        response = {}

        for class_id in CHALLENGE_CLASSES:
            challenge_class = CHALLENGE_CLASSES.get(class_id)
            response[challenge_class.id] = {
                'id': challenge_class.id,
                'name': challenge_class.name,
                'templates': challenge_class.templates,
                'scripts': challenge_class.scripts,
            }
        return response


@challenges_namespace.route('/<challenge_id>')
@challenges_namespace.param('challenge_id', 'A Challenge ID')
class Challenge(Resource):
    @during_ctf_time_only
    @require_verified_emails
    @viewable_without_authentication(status_code=403)
    def get(self, challenge_id):
        team_id = session.get('id')

        chal = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(chal.type)

        tags = [tag['value'] for tag in TagSchema("user", many=True).dump(chal.tags).data]
        files = [f.location for f in chal.files]
        unlocked_hints = set([u.item_id for u in Unlocks.query.filter_by(type='hints', team_id=team_id)])
        hints = []

        for hint in Hints.query.filter_by(challenge_id=chal.id).all():
            if hint.id in unlocked_hints or ctf_ended():
                hints.append({'id': hint.id, 'cost': hint.cost, 'hint': hint.hint})
            else:
                hints.append({'id': hint.id, 'cost': hint.cost})

        challenge, response = chal_class.read(challenge=chal)

        response['files'] = files
        response['tags'] = tags
        response['hints'] = hints

        db.session.close()
        return response

    # @admins_only
    # def put(self, challenge_id):
    #     challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    #     challenge_class = get_chal_class(challenge.type)
    #     challenge = challenge_class.update(challenge, request)
    #
    #     return challenge.read()

    @admins_only
    def patch(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        challenge_class = get_chal_class(challenge.type)
        challenge = challenge_class.update(challenge, request)
        challenge, response = challenge_class.read(challenge)
        return response

    @admins_only
    def delete(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(challenge.type)
        chal_class.delete(challenge)

        response = {
            'success': True,
        }
        return response


@challenges_namespace.route('/<challenge_id>/solves')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeSolves(Resource):
    @during_ctf_time_only
    @require_verified_emails
    @viewable_without_authentication(status_code=403)
    def get(self, challenge_id):
        response = []
        # if config.hide_scores():
        #     return jsonify(response)

        solves = Solves.query.join(Teams, Solves.team_id == Teams.id)\
            .filter(Solves.challenge_id == challenge_id, Teams.banned == False)\
            .order_by(Solves.date.asc())

        for solve in solves:
            response.append({
                'id': solve.team.id,
                'name': solve.team.name,
                'date': solve.date.isoformat()
            })

        return response


@challenges_namespace.route('/<challenge_id>/files')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeFiles(Resource):
    @admins_only
    def get(self, challenge_id):
        response = []

        challenge_files = ChallengeFilesModel.query.filter_by(challenge_id=challenge_id).all()

        for f in challenge_files:
            response.append({
                'id': f.id,
                'type': f.type,
                'location': f.location
            })
        return response


@challenges_namespace.route('/<challenge_id>/tags')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeFiles(Resource):
    @admins_only
    def get(self, challenge_id):
        response = []

        tags = Tags.query.filter_by(challenge_id=challenge_id).all()

        for t in tags:
            response.append({
                'id': t.id,
                'challenge_id': t.challenge_id,
                'value': t.value
            })
        return response


@challenges_namespace.route('/<challenge_id>/hints')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeHints(Resource):
    @admins_only
    def get(self, challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)

        return schema.dump(hints)


@challenges_namespace.route('/<challenge_id>/flags')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeFlags(Resource):
    @admins_only
    def get(self, challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)

        return schema.dump(flags)
