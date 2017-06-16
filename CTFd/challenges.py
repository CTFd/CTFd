import json
import logging
import re
import time

from flask import render_template, request, redirect, jsonify, url_for, session, Blueprint
from sqlalchemy.sql import or_

from CTFd.models import db, Challenges, Files, Solves, WrongKeys, Keys, Tags, Teams, Awards, Hints, Unlocks
from CTFd.plugins.keys import get_key_class
from CTFd.plugins.challenges import get_chal_class

from CTFd import utils

challenges = Blueprint('challenges', __name__)


@challenges.route('/hints/<int:hintid>', methods=['GET', 'POST'])
def hints_view(hintid):
    if not utils.ctf_started():
        abort(403)
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
        if not unlock and utils.ctftime():
            team = Teams.query.filter_by(id=session['id']).first()
            if team.score() < hint.cost:
                return jsonify({'errors': 'Not enough points'})
            unlock = Unlocks(model='hints', teamid=session['id'], itemid=hint.id)
            award = Awards(teamid=session['id'], name='Hint for {}'.format(chal.name), value=(-hint.cost))
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
        elif utils.ctf_ended():
            json_data = {
                'hint': hint.hint,
                'chal': hint.chal,
                'cost': hint.cost
            }
            db.session.close()
            return jsonify(json_data)
        else:
            json_data = {
                'hint': hint.hint,
                'chal': hint.chal,
                'cost': hint.cost
            }
            db.session.close()
            return jsonify(json_data)


@challenges.route('/challenges', methods=['GET'])
def challenges_view():
    errors = []
    start = utils.get_config('start') or 0
    end = utils.get_config('end') or 0
    if not utils.is_admin():  # User is not an admin
        if not utils.ctftime():
            # It is not CTF time
            if utils.view_after_ctf():  # But we are allowed to view after the CTF ends
                pass
            else:  # We are NOT allowed to view after the CTF ends
                if utils.get_config('start') and not utils.ctf_started():
                    errors.append('{} has not started yet'.format(utils.ctf_name()))
                if (utils.get_config('end') and utils.ctf_ended()) and not utils.view_after_ctf():
                    errors.append('{} has ended'.format(utils.ctf_name()))
                return render_template('chals.html', errors=errors, start=int(start), end=int(end))
        if utils.get_config('verify_emails') and not utils.is_verified():  # User is not confirmed
            return redirect(url_for('auth.confirm_user'))
    if utils.user_can_view_challenges():  # Do we allow unauthenticated users?
        if utils.get_config('start') and not utils.ctf_started():
            errors.append('{} has not started yet'.format(utils.ctf_name()))
        if (utils.get_config('end') and utils.ctf_ended()) and not utils.view_after_ctf():
            errors.append('{} has ended'.format(utils.ctf_name()))
        return render_template('chals.html', errors=errors, start=int(start), end=int(end))
    else:
        return redirect(url_for('auth.login', next='challenges'))


@challenges.route('/chals', methods=['GET'])
def chals():
    if not utils.is_admin():
        if not utils.ctftime():
            if utils.view_after_ctf():
                pass
            else:
                return redirect(url_for('views.static_html'))
    if utils.user_can_view_challenges() and (utils.ctf_started() or utils.is_admin()):
        chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None)).order_by(Challenges.value).all()
        json = {'game': []}
        for x in chals:
            tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=x.id).all()]
            files = [str(f.location) for f in Files.query.filter_by(chal=x.id).all()]
            unlocked_hints = set([u.itemid for u in Unlocks.query.filter_by(model='hints', teamid=session['id'])])
            hints = []
            for hint in Hints.query.filter_by(chal=x.id).all():
                if hint.id in unlocked_hints or utils.ctf_ended():
                    hints.append({'id': hint.id, 'cost': hint.cost, 'hint': hint.hint})
                else:
                    hints.append({'id': hint.id, 'cost': hint.cost})
            # hints = [{'id':hint.id, 'cost':hint.cost} for hint in Hints.query.filter_by(chal=x.id).all()]
            chal_type = get_chal_class(x.type)
            json['game'].append({
                'id': x.id,
                'type': chal_type.name,
                'name': x.name,
                'value': x.value,
                'description': x.description,
                'category': x.category,
                'files': files,
                'tags': tags,
                'hints': hints
            })

        db.session.close()
        return jsonify(json)
    else:
        db.session.close()
        return redirect(url_for('auth.login', next='chals'))


@challenges.route('/chals/solves')
def solves_per_chal():
    if not utils.user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))

    solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves')).join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False).group_by(Solves.chalid).subquery()
    solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves, Challenges.name) \
                       .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
    json = {}
    if utils.hide_scores():
        for chal, count, name in solves:
            json[chal] = -1
    else:
        for chal, count, name in solves:
            json[chal] = count
    db.session.close()
    return jsonify(json)


@challenges.route('/solves')
@challenges.route('/solves/<int:teamid>')
def solves(teamid=None):
    solves = None
    awards = None
    if teamid is None:
        if utils.is_admin():
            solves = Solves.query.filter_by(teamid=session['id']).all()
        elif utils.user_can_view_challenges():
            if utils.authed():
                solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.teamid == session['id'], Teams.banned == False).all()
            else:
                return jsonify({'solves': []})
        else:
            return redirect(url_for('auth.login', next='solves'))
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
    json = {'solves': []}
    for solve in solves:
        json['solves'].append({
            'chal': solve.chal.name,
            'chalid': solve.chalid,
            'team': solve.teamid,
            'value': solve.chal.value,
            'category': solve.chal.category,
            'time': utils.unix_time(solve.date)
        })
    if awards:
        for award in awards:
            json['solves'].append({
                'chal': award.name,
                'chalid': None,
                'team': award.teamid,
                'value': award.value,
                'category': award.category or "Award",
                'time': utils.unix_time(award.date)
            })
    json['solves'].sort(key=lambda k: k['time'])
    return jsonify(json)


@challenges.route('/maxattempts')
def attempts():
    if not utils.user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    chals = Challenges.query.add_columns('id').all()
    json = {'maxattempts': []}
    for chal, chalid in chals:
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        if fails >= int(utils.get_config("max_tries")) and int(utils.get_config("max_tries")) > 0:
            json['maxattempts'].append({'chalid': chalid})
    return jsonify(json)


@challenges.route('/fails/<int:teamid>', methods=['GET'])
def fails(teamid):
    fails = WrongKeys.query.filter_by(teamid=teamid).count()
    solves = Solves.query.filter_by(teamid=teamid).count()
    db.session.close()
    json = {'fails': str(fails), 'solves': str(solves)}
    return jsonify(json)


@challenges.route('/chal/<int:chalid>/solves', methods=['GET'])
def who_solved(chalid):
    if not utils.user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))

    json = {'teams': []}
    if utils.hide_scores():
        return jsonify(json)
    solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid == chalid, Teams.banned == False).order_by(Solves.date.asc())
    for solve in solves:
        json['teams'].append({'id': solve.team.id, 'name': solve.team.name, 'date': solve.date})
    return jsonify(json)


@challenges.route('/chal/<int:chalid>', methods=['POST'])
def chal(chalid):
    if utils.ctf_ended() and not utils.view_after_ctf():
        return redirect(url_for('challenges.challenges_view'))
    if not utils.user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    if utils.authed() and utils.is_verified() and (utils.ctf_started() or utils.view_after_ctf()):
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        logger = logging.getLogger('keys')
        data = (time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8'), request.form['key'].encode('utf-8'), utils.get_kpm(session['id']))
        print("[{0}] {1} submitted {2} with kpm {3}".format(*data))

        # Anti-bruteforce / submitting keys too quickly
        if utils.get_kpm(session['id']) > 10:
            if utils.ctftime():
                wrong = WrongKeys(session['id'], chalid, request.form['key'])
                db.session.add(wrong)
                db.session.commit()
                db.session.close()
            logger.warn("[{0}] {1} submitted {2} with kpm {3} [TOO FAST]".format(*data))
            # return '3' # Submitting too fast
            return jsonify({'status': 3, 'message': "You're submitting keys too fast. Slow down."})

        solves = Solves.query.filter_by(teamid=session['id'], chalid=chalid).first()

        # Challange not solved yet
        if not solves:
            chal = Challenges.query.filter_by(id=chalid).first_or_404()
            provided_key = request.form['key'].strip()
            saved_keys = Keys.query.filter_by(chal=chal.id).all()

            # Hit max attempts
            max_tries = chal.max_attempts
            if max_tries and fails >= max_tries > 0:
                return jsonify({
                    'status': 0,
                    'message': "You have 0 tries remaining"
                })

            chal_class = get_chal_class(chal.type)
            if chal_class.solve(chal, provided_key):
                if utils.ctftime():
                    solve = Solves(chalid=chalid, teamid=session['id'], ip=utils.get_ip(), flag=provided_key)
                    db.session.add(solve)
                    db.session.commit()
                    db.session.close()
                logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                return jsonify({'status': 1, 'message': 'Correct'})

            if utils.ctftime():
                wrong = WrongKeys(teamid=session['id'], chalid=chalid, flag=provided_key)
                db.session.add(wrong)
                db.session.commit()
                db.session.close()
            logger.info("[{0}] {1} submitted {2} with kpm {3} [WRONG]".format(*data))
            # return '0' # key was wrong
            if max_tries:
                attempts_left = max_tries - fails - 1  # Off by one since fails has changed since it was gotten
                tries_str = 'tries'
                if attempts_left == 1:
                    tries_str = 'try'
                return jsonify({'status': 0, 'message': 'Incorrect. You have {} {} remaining.'.format(attempts_left, tries_str)})
            else:
                return jsonify({'status': 0, 'message': 'Incorrect'})

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
