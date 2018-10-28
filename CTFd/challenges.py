from flask import render_template, request, redirect, jsonify, url_for, session, Blueprint, abort
from CTFd.models import db, Challenges, Files, Solves, Fails, Flags, Tags, Teams, Awards, Hints, Unlocks
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication,
    ratelimit,
    require_team
)
from CTFd.utils import config, text_type, user as current_user, get_config
from CTFd.utils.dates import ctftime, ctf_started, ctf_paused, ctf_ended, unix_time, unix_time_to_utc
from CTFd.utils.user import get_current_user, get_current_team
from sqlalchemy.sql import or_
import logging
import time

challenges = Blueprint('challenges', __name__)


# @challenges.route('/hints/<int:hintid>', methods=['GET', 'POST'])
# @during_ctf_time_only
# @authed_only
# def hints_view(hintid):
#     # TODO: Move this to the API
#     hint = Hints.query.filter_by(id=hintid).first_or_404()
#     chal = Challenges.query.filter_by(id=hint.chal).first()
#     unlock = Unlocks.query.filter_by(type='hints', item_id=hintid, team_id=session['id']).first()
#     if request.method == 'GET':
#         if unlock:
#             return jsonify({
#                 'hint': hint.hint,
#                 'chal': hint.chal,
#                 'cost': hint.cost
#             })
#         else:
#             return jsonify({
#                 'chal': hint.chal,
#                 'cost': hint.cost
#             })
#     elif request.method == 'POST':
#         if unlock is None:  # The user does not have an unlock.
#             if ctftime() or (ctf_ended() and config.view_after_ctf()) or current_user.is_admin() is True:
#                 # It's ctftime or the CTF has ended (but we allow views after)
#                 team = Teams.query.filter_by(id=session['id']).first()
#                 if team.score() < hint.cost:
#                     return jsonify({'errors': 'Not enough points'})
#                 unlock = Unlocks(model='hints', team_id=session['id'], item_id=hint.id)
#                 award = Awards(team_id=session['id'], name=text_type('Hint for {}'.format(chal.name)), value=(-hint.cost))
#                 db.session.add(unlock)
#                 db.session.add(award)
#                 db.session.commit()
#                 json_data = {
#                     'hint': hint.hint,
#                     'chal': hint.chal,
#                     'cost': hint.cost
#                 }
#                 db.session.close()
#                 return jsonify(json_data)
#             elif ctf_ended():  # The CTF has ended. No views after.
#                 abort(403)
#         else:  # The user does have an unlock, we should give them their hint.
#             json_data = {
#                 'hint': hint.hint,
#                 'chal': hint.chal,
#                 'cost': hint.cost
#             }
#             db.session.close()
#             return jsonify(json_data)


@challenges.route('/challenges', methods=['GET'])
@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication()
@require_team
def listing():
    infos = []
    errors = []
    start = get_config('start') or 0
    end = get_config('end') or 0

    if ctf_paused():
        infos.append('{} is paused'.format(config.ctf_name()))

    if not ctftime():
        # It is not CTF time
        if config.view_after_ctf():  # But we are allowed to view after the CTF ends
            pass
        else:  # We are NOT allowed to view after the CTF ends
            if get_config('start') and not ctf_started():
                errors.append('{} has not started yet'.format(config.ctf_name()))
            if (get_config('end') and ctf_ended()) and not config.view_after_ctf():
                errors.append('{} has ended'.format(config.ctf_name()))
            return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))

    return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))


# @challenges.route('/solves')
# @authed_only
# def solves_private():
#     # TODO: Move this to the API
#     solves = None
#     awards = None
#
#     if current_user.is_admin():
#         solves = Solves.query.filter_by(team_id=session['id']).all()
#     elif config.user_can_view_challenges():
#         if current_user.authed():
#             solves = Solves.query\
#                 .join(Teams, Solves.team_id == Teams.id)\
#                 .filter(Solves.team_id == session['id'])\
#                 .all()
#         else:
#             return jsonify({'solves': []})
#     else:
#         return redirect(url_for('auth.login', next='solves'))
#
#     db.session.close()
#     response = {'solves': []}
#     for solve in solves:
#         response['solves'].append({
#             'chal': solve.challenge.name,
#             'challenge_id': solve.challenge_id,
#             'team': solve.team_id,
#             'value': solve.chal.value,
#             'category': solve.chal.category,
#             'time': unix_time(solve.date)
#         })
#     if awards:
#         for award in awards:
#             response['solves'].append({
#                 'chal': award.name,
#                 'challenge_id': None,
#                 'team': award.team_id,
#                 'value': award.value,
#                 'category': award.category or "Award",
#                 'time': unix_time(award.date)
#             })
#     response['solves'].sort(key=lambda k: k['time'])
#     return jsonify(response)


# @challenges.route('/solves/<int:team_id>')
# def solves_public(team_id=None):
#     # TODO: Move this to the API
#     solves = None
#     awards = None
#
#     if current_user.authed() and session['id'] == team_id:
#         solves = Solves.query.filter_by(team_id=team_id)
#         awards = Awards.query.filter_by(team_id=team_id)
#
#         freeze = get_config('freeze')
#         if freeze:
#             freeze = unix_time_to_utc(freeze)
#             if team_id != session.get('id'):
#                 solves = solves.filter(Solves.date < freeze)
#                 awards = awards.filter(Awards.date < freeze)
#
#         solves = solves.all()
#         awards = awards.all()
#     elif config.hide_scores():
#         # Use empty values to hide scores
#         solves = []
#         awards = []
#     else:
#         solves = Solves.query.filter_by(team_id=team_id)
#         awards = Awards.query.filter_by(team_id=team_id)
#
#         freeze = get_config('freeze')
#         if freeze:
#             freeze = unix_time_to_utc(freeze)
#             if team_id != session.get('id'):
#                 solves = solves.filter(Solves.date < freeze)
#                 awards = awards.filter(Awards.date < freeze)
#
#         solves = solves.all()
#         awards = awards.all()
#     db.session.close()
#
#     response = {'solves': []}
#     for solve in solves:
#         response['solves'].append({
#             'chal': solve.challenge.name,
#             'challenge_id': solve.challenge_id,
#             'team': solve.team_id,
#             'value': solve.challenge.value,
#             'category': solve.challenge.category,
#             'time': unix_time(solve.date)
#         })
#     if awards:
#         for award in awards:
#             response['solves'].append({
#                 'chal': award.name,
#                 'challenge_id': None,
#                 'team': award.team_id,
#                 'value': award.value,
#                 'category': award.category or "Award",
#                 'time': unix_time(award.date)
#             })
#     response['solves'].sort(key=lambda k: k['time'])
#     return jsonify(response)
#
#
# @challenges.route('/fails')
# @authed_only
# def fails_private():
#     # TODO: Move this to the API
#     fails = Fails.query.filter_by(team_id=session['id']).count()
#     solves = Solves.query.filter_by(team_id=session['id']).count()
#
#     db.session.close()
#     response = {
#         'fails': str(fails),
#         'solves': str(solves)
#     }
#     return jsonify(response)
#
#
# @challenges.route('/fails/<int:team_id>')
# def fails_public(team_id=None):
#     # TODO: Move this to the API
#     if current_user.authed() and session['id'] == team_id:
#         fails = Fails.query.filter_by(team_id=team_id).count()
#         solves = Solves.query.filter_by(team_id=team_id).count()
#     elif config.hide_scores():
#         fails = 0
#         solves = 0
#     else:
#         fails = Fails.query.filter_by(team_id=team_id).count()
#         solves = Solves.query.filter_by(team_id=team_id).count()
#     db.session.close()
#     response = {
#         'fails': str(fails),
#         'solves': str(solves)
#     }
#     return jsonify(response)
