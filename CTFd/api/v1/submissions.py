from flask import session, jsonify, request, abort
from flask_restplus import Namespace, Resource, reqparse

from CTFd.models import db, Challenges, Unlocks, Fails, Solves, Teams, Flags, Submissions
from CTFd.utils import config
from CTFd.utils import user as current_user
from CTFd.utils.user import get_current_team
from CTFd.utils.user import get_current_user
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_started, ctf_ended, ctf_paused, ctftime
from CTFd.utils.logging import log
from CTFd.schemas.submissions import SubmissionSchema
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from sqlalchemy.sql import or_

import logging
import time

submissions_namespace = Namespace('submissions', description="Endpoint to retrieve Submission")


@submissions_namespace.route('')
class SubmissionsList(Resource):

    @admins_only
    def get(self):
        args = request.args.to_dict()
        schema = SubmissionSchema(many=True)
        if args:
            submissions = Submissions.query.filter_by(**args).all()
        else:
            submissions = Submissions.query.all()

        response = schema.dump(submissions)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @during_ctf_time_only
    @require_verified_emails
    # @ authed_only TODO: It's probably better to put authed_only here but I'm not sure the effects.
    def post(self):
        # TODO: This doesn't really conform to the JSON API
        if request.content_type != 'application/json':
            request_data = request.form
        else:
            request_data = request.get_json()

        challenge_id = request_data.get('challenge_id') or request_data.get('challenge_id')

        if ctf_paused():
            return {
                'status': 3,
                'message': '{} is paused'.format(config.ctf_name())
            }, 403

        if (current_user.authed() and (ctf_started() and ctftime())) or current_user.is_admin():
            user = get_current_user()
            team = get_current_team()

            fails = Fails.query.filter_by(
                account_id=user.account_id,
                challenge_id=challenge_id
            ).count()

            challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

            if challenge.state == 'hidden':
                abort(403)

            requirements = challenge.requirements
            if requirements:
                solve_ids = Solves.query \
                    .with_entities(Solves.challenge_id) \
                    .filter_by(account_id=user.account_id) \
                    .order_by(Solves.challenge_id.asc()) \
                    .all()

                prereqs = set(requirements.get('prerequisites', []))
                if solve_ids >= prereqs:
                    pass
                else:
                    abort(403)

            chal_class = get_chal_class(challenge.type)

            # Anti-bruteforce / submitting Flags too quickly
            if current_user.get_wrong_submissions_per_minute(session['id']) > 10:
                if ctftime():
                    chal_class.fail(
                        user=user,
                        team=team,
                        challenge=challenge,
                        request=request
                    )
                log(
                    'submissions',
                    "[{date}] {name} submitted {submission} with kpm {kpm} [TOO FAST]",
                    submission=request_data['submission'].encode('utf-8'),
                    kpm=current_user.get_wrong_submissions_per_minute(session['id'])
                )
                # Submitting too fast
                return {
                    'status': 3,
                    'message': "You're submitting Flags too fast. Slow down."
                }, 403

            solves = Solves.query.filter_by(
                account_id=user.account_id,
                challenge_id=challenge_id
            ).first()

            # Challenge not solved yet
            if not solves:
                # Hit max attempts
                max_tries = challenge.max_attempts
                if max_tries and fails >= max_tries > 0:
                    return {
                        'status': 0,
                        'message': "You have 0 tries remaining"
                    }, 403

                status, message = chal_class.attempt(challenge, request)
                if status:  # The challenge plugin says the input is right
                    if ctftime() or current_user.is_admin():
                        chal_class.solve(
                            user=user,
                            team=team,
                            challenge=challenge,
                            request=request
                        )

                    log(
                        'submissions',
                        "[{date}] {name} submitted {submission} with kpm {kpm} [CORRECT]",
                        submission=request_data['submission'].encode('utf-8'),
                        kpm=current_user.get_wrong_submissions_per_minute(session['id'])
                    )
                    return {
                        'status': 1,
                        'message': message
                    }
                else:  # The challenge plugin says the input is wrong
                    if ctftime() or current_user.is_admin():
                        chal_class.fail(
                            user=user,
                            team=team,
                            challenge=challenge,
                            request=request
                        )

                    log(
                        'submissions',
                        "[{date}] {name} submitted {submission} with kpm {kpm} [WRONG]",
                        submission=request_data['submission'].encode('utf-8'),
                        kpm=current_user.get_wrong_submissions_per_minute(session['id'])
                    )

                    if max_tries:
                        attempts_left = max_tries - fails - 1  # Off by one since fails has changed since it was gotten
                        tries_str = 'tries'
                        if attempts_left == 1:
                            tries_str = 'try'
                        if message[-1] not in '!().;?[]\{\}':  # Add a punctuation mark if there isn't one
                            message = message + '.'
                        return {
                            'status': 0,
                            'message': '{} You have {} {} remaining.'.format(message, attempts_left, tries_str)
                        }
                    else:
                        return {
                            'status': 0,
                            'message': message
                        }

            # Challenge already solved
            else:
                log(
                    'submissions',
                    "[{date}] {name} submitted {submission} with kpm {kpm} [ALREADY SOLVED]",
                    submission=request_data['submission'].encode('utf-8'),
                    kpm=current_user.get_wrong_submissions_per_minute(session['id'])
                )
                return {
                    'status': 2,
                    'message': 'You already solved this'
                }
        else:
            return {
                'status': -1,
                'message': "You must be logged in to solve a challenge"
            }, 302


@submissions_namespace.route('/<submission_id>')
@submissions_namespace.param('submission_id', 'A Submission ID')
class Submission(Resource):
    @admins_only
    def get(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        schema = SubmissionSchema()
        response = schema.dump(submission)

        if response.errors:
            return {
                'success': False,
                'errors': response.errors
            }, 400

        return {
            'success': True,
            'data': response.data
        }

    @admins_only
    def delete(self, submission_id):
        submission = Submissions.query.filter_by(id=submission_id).first_or_404()
        db.session.delete(submission)
        db.session.commit()
        db.session.close()

        return {
            'success': True
        }
