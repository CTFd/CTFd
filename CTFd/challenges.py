import json
import logging
import re
import time

from flask import render_template, request, redirect, jsonify, url_for, session, Blueprint, abort
from sqlalchemy.sql import or_

from CTFd.models import db, Challenges, Files, Solves, WrongKeys, Keys, Tags, Teams, Awards, Hints, Unlocks
from CTFd.plugins.keys import get_key_class
from CTFd.plugins.challenges import get_chal_class

from CTFd import utils
from CTFd.utils.decorators import (
    authed_only,
    admins_only,
    during_ctf_time_only,
    require_verified_emails,
    viewable_without_authentication
)
from CTFd.utils import text_type

challenges = Blueprint('challenges', __name__)


@challenges.route('/hints/<int:hintid>', methods=['GET', 'POST'])
@during_ctf_time_only
@authed_only
def hints_view(hintid):
    hint = Hints.query.filter_by(id=hintid).first_or_404()
    chal = Challenges.query.filter_by(id=hint.chal).first()
    unlock = Unlocks.query.filter_by(model='hints', itemid=hintid, teamid=session['id']).first()
    if request.method == 'GET':
        if unlock:
            return jsonify({
                'hint': hint.hint,
                'chal': hint.chal,
                'cost': hint.cost
            })
        else:
            return jsonify({
                'chal': hint.chal,
                'cost': hint.cost
            })
    elif request.method == 'POST':
        if unlock is None:  # The user does not have an unlock.
            if utils.ctftime() or (utils.ctf_ended() and utils.view_after_ctf()) or utils.is_admin() is True:
                # It's ctftime or the CTF has ended (but we allow views after)
                team = Teams.query.filter_by(id=session['id']).first()
                if team.score() < hint.cost:
                    return jsonify({'errors': 'Not enough points'})
                unlock = Unlocks(model='hints', teamid=session['id'], itemid=hint.id)
                award = Awards(teamid=session['id'], name=text_type('Hint for {}'.format(chal.name)), value=(-hint.cost))
                db.session.add(unlock)
                db.session.add(award)
                db.session.commit()
                json_data = {
                    'hint': hint.hint,
                    'chal': hint.chal,
                    'cost': hint.cost
                }
                db.session.close()
                return jsonify(json_data)
            elif utils.ctf_ended():  # The CTF has ended. No views after.
                abort(403)
        else:  # The user does have an unlock, we should give them their hint.
            json_data = {
                'hint': hint.hint,
                'chal': hint.chal,
                'cost': hint.cost
            }
            db.session.close()
            return jsonify(json_data)


@challenges.route('/challenges', methods=['GET'])
@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication()
def challenges_view():
    infos = []
    errors = []
    start = utils.get_config('start') or 0
    end = utils.get_config('end') or 0

    if utils.ctf_paused():
        infos.append('{} is paused'.format(utils.ctf_name()))

    if not utils.ctftime():
        # It is not CTF time
        if utils.view_after_ctf():  # But we are allowed to view after the CTF ends
            pass
        else:  # We are NOT allowed to view after the CTF ends
            if utils.get_config('start') and not utils.ctf_started():
                errors.append('{} has not started yet'.format(utils.ctf_name()))
            if (utils.get_config('end') and utils.ctf_ended()) and not utils.view_after_ctf():
                errors.append('{} has ended'.format(utils.ctf_name()))
            return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))

    return render_template('challenges.html', infos=infos, errors=errors, start=int(start), end=int(end))


@challenges.route('/chals', methods=['GET'])
@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication(status_code=403)
def chals():
    db_chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None)).order_by(Challenges.value).all()
    response = {'game': []}
    for chal in db_chals:
        tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal.id).all()]
        chal_type = get_chal_class(chal.type)
        response['game'].append({
            'id': chal.id,
            'type': chal_type.name,
            'name': chal.name,
            'value': chal.value,
            'category': chal.category,
            'tags': tags,
            'template': chal_type.templates['modal'],
            'script': chal_type.scripts['modal'],
        })

    db.session.close()
    return jsonify(response)


@challenges.route('/chals/<int:chal_id>', methods=['GET'])
@during_ctf_time_only
@require_verified_emails
@viewable_without_authentication(status_code=403)
def chal_view(chal_id):
    teamid = session.get('id')

    chal = Challenges.query.filter_by(id=chal_id).first_or_404()
    if chal.hidden:
        abort(404)
    chal_class = get_chal_class(chal.type)

    tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal.id).all()]
    files = [str(f.location) for f in Files.query.filter_by(chal=chal.id).all()]
    unlocked_hints = set([u.itemid for u in Unlocks.query.filter_by(model='hints', teamid=teamid)])
    hints = []

    for hint in Hints.query.filter_by(chal=chal.id).all():
        if hint.id in unlocked_hints or utils.ctf_ended():
            hints.append({'id': hint.id, 'cost': hint.cost, 'hint': hint.hint})
        else:
            hints.append({'id': hint.id, 'cost': hint.cost})

    challenge, response = chal_class.read(challenge=chal)

    response['files'] = files
    response['tags'] = tags
    response['hints'] = hints

    db.session.close()
    return jsonify(response)


@challenges.route('/chals/solves')
@viewable_without_authentication(status_code=403)
def solves_per_chal():
    chals = Challenges.query\
        .filter(or_(Challenges.hidden != True, Challenges.hidden == None))\
        .order_by(Challenges.value)\
        .all()

    solves_sub = db.session.query(
        Solves.chalid,
        db.func.count(Solves.chalid).label('solves')
    )\
        .join(Teams, Solves.teamid == Teams.id) \
        .filter(Teams.banned == False) \
        .group_by(Solves.chalid).subquery()

    solves = db.session.query(
        solves_sub.columns.chalid,
        solves_sub.columns.solves,
        Challenges.name
    ) \
        .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()

    data = {}
    if utils.hide_scores():
        for chal, count, name in solves:
            data[chal] = -1
        for c in chals:
            if c.id not in data:
                data[c.id] = -1
    else:
        for chal, count, name in solves:
            data[chal] = count
        for c in chals:
            if c.id not in data:
                data[c.id] = 0
    db.session.close()
    return jsonify(data)


@challenges.route('/solves')
@authed_only
def solves_private():
    solves = None
    awards = None

    if utils.is_admin():
        solves = Solves.query.filter_by(teamid=session['id']).all()
    elif utils.user_can_view_challenges():
        if utils.authed():
            solves = Solves.query\
                .join(Teams, Solves.teamid == Teams.id)\
                .filter(Solves.teamid == session['id'])\
                .all()
        else:
            return jsonify({'solves': []})
    else:
        return redirect(url_for('auth.login', next='solves'))

    db.session.close()
    response = {'solves': []}
    for solve in solves:
        response['solves'].append({
            'chal': solve.chal.name,
            'chalid': solve.chalid,
            'team': solve.teamid,
            'value': solve.chal.value,
            'category': solve.chal.category,
            'time': utils.unix_time(solve.date)
        })
    if awards:
        for award in awards:
            response['solves'].append({
                'chal': award.name,
                'chalid': None,
                'team': award.teamid,
                'value': award.value,
                'category': award.category or "Award",
                'time': utils.unix_time(award.date)
            })
    response['solves'].sort(key=lambda k: k['time'])
    return jsonify(response)


@challenges.route('/solves/<int:teamid>')
def solves_public(teamid=None):
    solves = None
    awards = None

    if utils.authed() and session['id'] == teamid:
        solves = Solves.query.filter_by(teamid=teamid)
        awards = Awards.query.filter_by(teamid=teamid)

        freeze = utils.get_config('freeze')
        if freeze:
            freeze = utils.unix_time_to_utc(freeze)
            if teamid != session.get('id'):
                solves = solves.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        solves = solves.all()
        awards = awards.all()
    elif utils.hide_scores():
        # Use empty values to hide scores
        solves = []
        awards = []
    else:
        solves = Solves.query.filter_by(teamid=teamid)
        awards = Awards.query.filter_by(teamid=teamid)

        freeze = utils.get_config('freeze')
        if freeze:
            freeze = utils.unix_time_to_utc(freeze)
            if teamid != session.get('id'):
                solves = solves.filter(Solves.date < freeze)
                awards = awards.filter(Awards.date < freeze)

        solves = solves.all()
        awards = awards.all()
    db.session.close()

    response = {'solves': []}
    for solve in solves:
        response['solves'].append({
            'chal': solve.chal.name,
            'chalid': solve.chalid,
            'team': solve.teamid,
            'value': solve.chal.value,
            'category': solve.chal.category,
            'time': utils.unix_time(solve.date)
        })
    if awards:
        for award in awards:
            response['solves'].append({
                'chal': award.name,
                'chalid': None,
                'team': award.teamid,
                'value': award.value,
                'category': award.category or "Award",
                'time': utils.unix_time(award.date)
            })
    response['solves'].sort(key=lambda k: k['time'])
    return jsonify(response)


@challenges.route('/fails')
@authed_only
def fails_private():
    fails = WrongKeys.query.filter_by(teamid=session['id']).count()
    solves = Solves.query.filter_by(teamid=session['id']).count()

    db.session.close()
    response = {
        'fails': str(fails),
        'solves': str(solves)
    }
    return jsonify(response)


@challenges.route('/fails/<int:teamid>')
def fails_public(teamid=None):
    if utils.authed() and session['id'] == teamid:
        fails = WrongKeys.query.filter_by(teamid=teamid).count()
        solves = Solves.query.filter_by(teamid=teamid).count()
    elif utils.hide_scores():
        fails = 0
        solves = 0
    else:
        fails = WrongKeys.query.filter_by(teamid=teamid).count()
        solves = Solves.query.filter_by(teamid=teamid).count()
    db.session.close()
    response = {
        'fails': str(fails),
        'solves': str(solves)
    }
    return jsonify(response)


@challenges.route('/chal/<int:chalid>/solves', methods=['GET'])
@during_ctf_time_only
@viewable_without_authentication(status_code=403)
def who_solved(chalid):
    response = {'teams': []}
    if utils.hide_scores():
        return jsonify(response)
    solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid == chalid, Teams.banned == False).order_by(Solves.date.asc())
    for solve in solves:
        response['teams'].append({'id': solve.team.id, 'name': solve.team.name, 'date': solve.date})
    return jsonify(response)


@challenges.route('/chal/<int:chalid>', methods=['POST'])
@during_ctf_time_only
@viewable_without_authentication()
def chal(chalid):
    if utils.ctf_paused():
        return jsonify({
            'status': 3,
            'message': '{} is paused'.format(utils.ctf_name())
        })
    if (utils.authed() and utils.is_verified() and (utils.ctf_started() or utils.view_after_ctf())) or utils.is_admin():
        team = Teams.query.filter_by(id=session['id']).first()
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        logger = logging.getLogger('keys')
        data = (time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8'), request.form['key'].encode('utf-8'), utils.get_kpm(session['id']))
        print("[{0}] {1} submitted {2} with kpm {3}".format(*data))

        chal = Challenges.query.filter_by(id=chalid).first_or_404()
        if chal.hidden:
            abort(404)
        chal_class = get_chal_class(chal.type)

        # Anti-bruteforce / submitting keys too quickly
        if utils.get_kpm(session['id']) > 10:
            if utils.ctftime():
                chal_class.fail(team=team, chal=chal, request=request)
            logger.warn("[{0}] {1} submitted {2} with kpm {3} [TOO FAST]".format(*data))
            # return '3' # Submitting too fast
            return jsonify({'status': 3, 'message': "You're submitting keys too fast. Slow down."})

        solves = Solves.query.filter_by(teamid=session['id'], chalid=chalid).first()

        # Challange not solved yet
        if not solves:
            provided_key = request.form['key'].strip()
            saved_keys = Keys.query.filter_by(chal=chal.id).all()

            # Hit max attempts
            max_tries = chal.max_attempts
            if max_tries and fails >= max_tries > 0:
                return jsonify({
                    'status': 0,
                    'message': "You have 0 tries remaining"
                })

            status, message = chal_class.attempt(chal, request)
            if status:  # The challenge plugin says the input is right
                if utils.ctftime() or utils.is_admin():
                    chal_class.solve(team=team, chal=chal, request=request)
                logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                return jsonify({'status': 1, 'message': message})
            else:  # The challenge plugin says the input is wrong
                if utils.ctftime() or utils.is_admin():
                    chal_class.fail(team=team, chal=chal, request=request)
                logger.info("[{0}] {1} submitted {2} with kpm {3} [WRONG]".format(*data))
                # return '0' # key was wrong
                if max_tries:
                    attempts_left = max_tries - fails - 1  # Off by one since fails has changed since it was gotten
                    tries_str = 'tries'
                    if attempts_left == 1:
                        tries_str = 'try'
                    if message[-1] not in '!().;?[]\{\}':  # Add a punctuation mark if there isn't one
                        message = message + '.'
                    return jsonify({'status': 0, 'message': '{} You have {} {} remaining.'.format(message, attempts_left, tries_str)})
                else:
                    return jsonify({'status': 0, 'message': message})

        # Challenge already solved
        else:
            logger.info("{0} submitted {1} with kpm {2} [ALREADY SOLVED]".format(*data))
            # return '2' # challenge was already solved
            return jsonify({'status': 2, 'message': 'You already solved this'})
    else:
        return jsonify({
            'status': -1,
            'message': "You must be logged in to solve a challenge"
        })
