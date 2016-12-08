from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint

from CTFd.utils import ctftime, view_after_ctf, authed, unix_time, get_kpm, user_can_view_challenges, is_admin, get_config, get_ip, is_verified, ctf_started, ctf_ended, ctf_name
from CTFd.models import db, Challenges, Files, Solves, WrongKeys, Keys, Tags, Teams, Awards

from sqlalchemy.sql import and_, or_, not_

import time
import re
import logging
import json

challenges = Blueprint('challenges', __name__)


@challenges.route('/challenges', methods=['GET'])
def challenges_view():
    errors = []
    start = get_config('start') or 0
    end = get_config('end') or 0
    if not is_admin(): # User is not an admin
        if not ctftime():
            # It is not CTF time
            if view_after_ctf(): # But we are allowed to view after the CTF ends
                pass
            else:  # We are NOT allowed to view after the CTF ends
                if get_config('start') and not ctf_started():
                    errors.append('{} has not started yet'.format(ctf_name()))
                if (get_config('end') and ctf_ended()) and not view_after_ctf():
                    errors.append('{} has ended'.format(ctf_name()))
                return render_template('chals.html', errors=errors, start=int(start), end=int(end))
        if get_config('verify_emails') and not is_verified(): # User is not confirmed
            return redirect(url_for('auth.confirm_user'))
    if user_can_view_challenges(): # Do we allow unauthenticated users?
        if get_config('start') and not ctf_started():
            errors.append('{} has not started yet'.format(ctf_name()))
        if (get_config('end') and ctf_ended()) and not view_after_ctf():
            errors.append('{} has ended'.format(ctf_name()))
        return render_template('chals.html', errors=errors, start=int(start), end=int(end))
    else:
        return redirect(url_for('auth.login', next='challenges'))


@challenges.route('/chals', methods=['GET'])
def chals():
    if not is_admin():
        if not ctftime():
            if view_after_ctf():
                pass
            else:
                return redirect(url_for('views.static_html'))
    if user_can_view_challenges() and (ctf_started() or is_admin()):
        chals = Challenges.query.filter(or_(Challenges.hidden != True, Challenges.hidden == None)).add_columns('id', 'name', 'value', 'description', 'category').order_by(Challenges.value).all()

        json = {'game':[]}
        for x in chals:
            tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=x[1]).all()]
            files = [ str(f.location) for f in Files.query.filter_by(chal=x.id).all() ]
            json['game'].append({'id':x[1], 'name':x[2], 'value':x[3], 'description':x[4], 'category':x[5], 'files':files, 'tags':tags})

        db.session.close()
        return jsonify(json)
    else:
        db.session.close()
        return redirect(url_for('auth.login', next='chals'))


@challenges.route('/chals/solves')
def chals_per_solves():
    if not user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    solves_sub = db.session.query(Solves.chalid, db.func.count(Solves.chalid).label('solves')).join(Teams, Solves.teamid == Teams.id).filter(Teams.banned == False).group_by(Solves.chalid).subquery()
    solves = db.session.query(solves_sub.columns.chalid, solves_sub.columns.solves, Challenges.name) \
        .join(Challenges, solves_sub.columns.chalid == Challenges.id).all()
    json = {}
    for chal, count, name in solves:
        json[chal] = count
    db.session.close()
    return jsonify(json)



@challenges.route('/solves')
@challenges.route('/solves/<teamid>')
def solves(teamid=None):
    solves = None
    awards = None
    if teamid is None:
        if is_admin():
            solves = Solves.query.filter_by(teamid=session['id']).all()
        elif authed():
            solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.teamid == session['id'], Teams.banned == False).all()
        else:
            return redirect(url_for('auth.login', next='solves'))
    else:
        solves = Solves.query.filter_by(teamid=teamid).all()
        awards = Awards.query.filter_by(teamid=teamid).all()
    db.session.close()
    json = {'solves':[]}
    for solve in solves:
        json['solves'].append({
            'chal': solve.chal.name,
            'chalid': solve.chalid,
            'team': solve.teamid,
            'value': solve.chal.value,
            'category': solve.chal.category,
            'time': unix_time(solve.date)
        })
    if awards:
        for award in awards:
            json['solves'].append({
                'chal': award.name,
                'chalid': None,
                'team': award.teamid,
                'value': award.value,
                'category': award.category,
                'time': unix_time(award.date)
            })
    json['solves'].sort(key=lambda k: k['time'])
    return jsonify(json)


@challenges.route('/maxattempts')
def attempts():
    if not user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    chals = Challenges.query.add_columns('id').all()
    json = {'maxattempts':[]}
    for chal, chalid in chals:
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        if fails >= int(get_config("max_tries")) and int(get_config("max_tries")) > 0:
            json['maxattempts'].append({'chalid':chalid})
    return jsonify(json)


@challenges.route('/fails/<teamid>', methods=['GET'])
def fails(teamid):
    fails = WrongKeys.query.filter_by(teamid=teamid).count()
    solves = Solves.query.filter_by(teamid=teamid).count()
    db.session.close()
    json = {'fails':str(fails), 'solves': str(solves)}
    return jsonify(json)


@challenges.route('/chal/<chalid>/solves', methods=['GET'])
def who_solved(chalid):
    if not user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid == chalid, Teams.banned == False).order_by(Solves.date.asc())
    json = {'teams':[]}
    for solve in solves:
        json['teams'].append({'id':solve.team.id, 'name':solve.team.name, 'date':solve.date})
    return jsonify(json)


@challenges.route('/chal/<chalid>', methods=['POST'])
def chal(chalid):
    if ctf_ended() and not view_after_ctf():
        return redirect(url_for('challenges.challenges_view'))
    if not user_can_view_challenges():
        return redirect(url_for('auth.login', next=request.path))
    if authed() and is_verified() and (ctf_started() or view_after_ctf()):
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        logger = logging.getLogger('keys')
        data = (time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8'), request.form['key'].encode('utf-8'), get_kpm(session['id']))
        print("[{0}] {1} submitted {2} with kpm {3}".format(*data))

        # Anti-bruteforce / submitting keys too quickly
        if get_kpm(session['id']) > 10:
            if ctftime():
                wrong = WrongKeys(session['id'], chalid, request.form['key'])
                db.session.add(wrong)
                db.session.commit()
                db.session.close()
            logger.warn("[{0}] {1} submitted {2} with kpm {3} [TOO FAST]".format(*data))
            # return "3" # Submitting too fast
            return jsonify({'status': '3', 'message': "You're submitting keys too fast. Slow down."})

        solves = Solves.query.filter_by(teamid=session['id'], chalid=chalid).first()

        # Challange not solved yet
        if not solves:
            chal = Challenges.query.filter_by(id=chalid).first()
            key = unicode(request.form['key'].strip().lower())
            keys = json.loads(chal.flags)

            # Hit max attempts
            max_tries = int(get_config("max_tries"))
            if fails >= max_tries > 0:
                return jsonify({
                    'status': '0',
                    'message': "You have 0 tries remaining"
                })

            for x in keys:
                if x['type'] == 0: #static key
                    print(x['flag'], key.strip().lower())
                    if x['flag'] and x['flag'].strip().lower() == key.strip().lower():
                        if ctftime():
                            solve = Solves(chalid=chalid, teamid=session['id'], ip=get_ip(), flag=key)
                            db.session.add(solve)
                            db.session.commit()
                            db.session.close()
                        logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        # return "1" # key was correct
                        return jsonify({'status':'1', 'message':'Correct'})
                elif x['type'] == 1: #regex
                    res = re.match(x['flag'], key, re.IGNORECASE)
                    if res and res.group() == key:
                        if ctftime():
                            solve = Solves(chalid=chalid, teamid=session['id'], ip=get_ip(), flag=key)
                            db.session.add(solve)
                            db.session.commit()
                            db.session.close()
                        logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        # return "1" # key was correct
                        return jsonify({'status': '1', 'message': 'Correct'})

            if ctftime():
                wrong = WrongKeys(session['id'], chalid, request.form['key'])
                db.session.add(wrong)
                db.session.commit()
                db.session.close()
            logger.info("[{0}] {1} submitted {2} with kpm {3} [WRONG]".format(*data))
            # return '0' # key was wrong
            if max_tries:
                attempts_left = max_tries - fails
                tries_str = 'tries'
                if attempts_left == 1:
                    tries_str = 'try'
                return jsonify({'status': '0', 'message': 'Incorrect. You have {} {} remaining.'.format(attempts_left, tries_str)})
            else:
                return jsonify({'status': '0', 'message': 'Incorrect'})


        # Challenge already solved
        else:
            logger.info("{0} submitted {1} with kpm {2} [ALREADY SOLVED]".format(*data))
            # return "2" # challenge was already solved
            return jsonify({'status': '2', 'message': 'You already solved this'})
    else:
        return "-1"
