from flask import session, request, abort
from flask_restplus import Namespace, Resource
from CTFd.models import (
    db,
    Challenges,
    Unlocks,
    Tags,
    Hints,
    Flags,
    Solves,
    ChallengeFiles as ChallengeFilesModel,
)
from CTFd.plugins.challenges import get_chal_class, CHALLENGE_CLASSES
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import (
    during_ctf_time_only,
    require_verified_emails,
    admins_only
)
from CTFd.utils.decorators.visibility import (
    check_challenge_visibility,
    check_score_visibility
)
from CTFd.utils.config.visibility import scores_visible, accounts_visible
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.modes import get_model
from CTFd.schemas.tags import TagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.flags import FlagSchema
from sqlalchemy.sql import or_, and_, any_

challenges_namespace = Namespace('challenges', description="Endpoint to retrieve Challenges")


@challenges_namespace.route('')
class ChallengeList(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    def get(self):
        # This can return None (unauth) if visibility is set to public
        user = get_current_user()

        challenges = Challenges.query.filter(
            and_(Challenges.state != 'hidden', Challenges.state != 'locked')
        ).order_by(Challenges.value).all()

        if user:
            solve_ids = Solves.query\
                .with_entities(Solves.challenge_id)\
                .filter_by(account_id=user.account_id)\
                .order_by(Solves.challenge_id.asc())\
                .all()
            solve_ids = set([value for value, in solve_ids])
        else:
            solve_ids = set()

        response = []
        tag_schema = TagSchema(view='user', many=True)
        for challenge in challenges:
            requirements = challenge.requirements
            if requirements:
                prereqs = set(requirements.get('prerequisites', []))
                anonymize = requirements.get('anonymize')
                if solve_ids >= prereqs:
                    pass
                else:
                    if anonymize:
                        response.append({
                            'id': challenge.id,
                            'type': 'hidden',
                            'name': '???',
                            'value': 0,
                            'category': '???',
                            'tags': [],
                            'template': '',
                            'script': ''
                        })
                    # Fallthrough to continue
                    continue

            challenge_type = get_chal_class(challenge.type)
            response.append({
                'id': challenge.id,
                'type': challenge_type.name,
                'name': challenge.name,
                'value': challenge.value,
                'category': challenge.category,
                'tags': tag_schema.dump(challenge.tags).data,
                'template': challenge_type.templates['view'],
                'script': challenge_type.scripts['view'],
            })

        db.session.close()
        return {
            'success': True,
            'data': response
        }

    @admins_only
    def post(self):
        data = request.form or request.get_json()
        challenge_type = data['type']
        challenge_class = get_chal_class(challenge_type)
        challenge = challenge_class.create(request)
        response = challenge_class.read(challenge)
        return {
            'success': True,
            'data': response
        }


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
        return {
            'success': True,
            'data': response
        }


@challenges_namespace.route('/<challenge_id>')
@challenges_namespace.param('challenge_id', 'A Challenge ID')
class Challenge(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
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

        response = chal_class.read(challenge=chal)

        Model = get_model()

        if scores_visible() is True and accounts_visible() is True:
            solves = Solves.query\
                .join(Model, Solves.account_id == Model.id)\
                .filter(Solves.challenge_id == chal.id, Model.banned == False, Model.hidden == False)\
                .count()
            response['solves'] = solves
        else:
            response['solves'] = None

        response['files'] = files
        response['tags'] = tags
        response['hints'] = hints

        db.session.close()
        return {
            'success': True,
            'data': response
        }

    @admins_only
    def patch(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        challenge_class = get_chal_class(challenge.type)
        challenge = challenge_class.update(challenge, request)
        response = challenge_class.read(challenge)
        return {
            'success': True,
            'data': response
        }

    @admins_only
    def delete(self, challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(challenge.type)
        chal_class.delete(challenge)

        return {
            'success': True,
        }


@challenges_namespace.route('/<challenge_id>/solves')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeSolves(Resource):
    @check_challenge_visibility
    @check_score_visibility
    @during_ctf_time_only
    @require_verified_emails
    def get(self, challenge_id):
        response = []
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        # TODO: Need a generic challenge visibility call.
        if challenge.state == 'hidden' and is_admin() is False:
            abort(404)

        Model = get_model()

        solves = Solves.query.join(Model, Solves.account_id == Model.id)\
            .filter(Solves.challenge_id == challenge_id, Model.banned == False, Model.hidden == False)\
            .order_by(Solves.date.asc())

        for solve in solves:
            response.append({
                'account_id': solve.account_id,
                'name': solve.account.name,
                'date': solve.date.isoformat()
            })

        return {
            'success': True,
            'data': response
        }


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
        return {
            'success': True,
            'data': response
        }


@challenges_namespace.route('/<challenge_id>/tags')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeTags(Resource):
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
        return {
            'success': True,
            'data': response
        }


@challenges_namespace.route('/<challenge_id>/hints')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeHints(Resource):
    @admins_only
    def get(self, challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)
        response = schema.dump(hints)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }


@challenges_namespace.route('/<challenge_id>/flags')
@challenges_namespace.param('id', 'A Challenge ID')
class ChallengeFlags(Resource):
    @admins_only
    def get(self, challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }
