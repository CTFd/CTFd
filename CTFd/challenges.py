from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint

from CTFd.utils import ctftime, view_after_ctf, authed, unix_time, get_kpm, can_view_challenges, is_admin, get_config, get_ip, is_verified
from CTFd.models import db, Challenges, Files, Solves, WrongKeys, Keys, Tags, Teams, Awards

from sqlalchemy.sql import and_, or_, not_

import time
import re
import logging
import json

challenges = Blueprint('challenges', __name__)


@challenges.route('/challenges', methods=['GET'])
def challenges_view():
    if not is_admin():
        if not ctftime():
            if view_after_ctf():
                pass
            else:
                return redirect('/')
        if get_config('verify_emails') and not is_verified():
            return redirect(url_for('auth.confirm_user'))
    if can_view_challenges():
        return render_template('chals.html', ctftime=ctftime())
    else:
        return redirect(url_for('auth.login', next='challenges'))


@challenges.route('/chals', methods=['GET'])
def chals():
    if not is_admin():
        if not ctftime():
            if view_after_ctf():
                pass
            else:
                return redirect('/')
    if can_view_challenges():
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
    if can_view_challenges():
        solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Teams.banned==None).add_columns(db.func.count(Solves.chalid)).group_by(Solves.chalid).all()
        json = {}
        for chal, count in solves:
            json[chal.chal.name] = count
        return jsonify(json)
    return redirect(url_for('auth.login', next='chals/solves'))


@challenges.route('/solves')
@challenges.route('/solves/<teamid>')
def solves(teamid=None):
    if teamid is None:
        if is_admin():
            solves = Solves.query.filter_by(teamid=session['id']).all()
        elif authed():
            solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.teamid==session['id'], Teams.banned==None).all()
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
    solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid==chalid, Teams.banned==None).order_by(Solves.date.asc())
    json = {'teams':[]}
    for solve in solves:
        json['teams'].append({'id':solve.team.id, 'name':solve.team.name, 'date':solve.date})
    return jsonify(json)


@challenges.route('/chal/<chalid>', methods=['POST'])
def chal(chalid):
    if not ctftime():
        return redirect(url_for('challenges.challenges_view'))
    if authed():
        fails = WrongKeys.query.filter_by(teamid=session['id'], chalid=chalid).count()
        logger = logging.getLogger('keys')
        data = (time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8'), request.form['key'].encode('utf-8'), get_kpm(session['id']))
        print("[{0}] {1} submitted {2} with kpm {3}".format(*data))

        # Hit max attempts
        if fails >= int(get_config("max_tries")) and int(get_config("max_tries")) > 0:
            return "4" #too many tries on this challenge

        # Anti-bruteforce / submitting keys too quickly
        if get_kpm(session['id']) > 10:
            wrong = WrongKeys(session['id'], chalid, request.form['key'])
            db.session.add(wrong)
            db.session.commit()
            db.session.close()
            logger.warn("[{0}] {1} submitted {2} with kpm {3} [TOO FAST]".format(*data))
            return "3" # Submitting too fast

        solves = Solves.query.filter_by(teamid=session['id'], chalid=chalid).first()

        # Challange not solved yet
        if not solves:
            chal = Challenges.query.filter_by(id=chalid).first()
            key = str(request.form['key'].strip().lower())
            keys = json.loads(chal.flags)
            for x in keys:
                if x['type'] == 0: #static key
                    print(x['flag'], key.strip().lower())
                    if x['flag'] and x['flag'].strip().lower() == key.strip().lower():
                        solve = Solves(chalid=chalid, teamid=session['id'], ip=get_ip(), flag=key)
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                        logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        return "1" # key was correct
                elif x['type'] == 1: #regex
                    res = re.match(str(x['flag']), key, re.IGNORECASE)
                    if res and res.group() == key:
                        solve = Solves(chalid=chalid, teamid=session['id'], ip=get_ip(), flag=key)
                        db.session.add(solve)
                        db.session.commit()
                        db.session.close()
                        logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                        return "1" # key was correct

            wrong = WrongKeys(session['id'], chalid, request.form['key'])
            db.session.add(wrong)
            db.session.commit()
            db.session.close()
            logger.info("[{0}] {1} submitted {2} with kpm {3} [WRONG]".format(*data))
            return '0' # key was wrong

        # Challenge already solved
        else:
            logger.info("{0} submitted {1} with kpm {2} [ALREADY SOLVED]".format(*data))
            return "2" # challenge was already solved
    else:
        return "-1"
