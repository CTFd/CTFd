from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session

from CTFd.utils import ctftime, authed, unix_time, get_kpm, can_view_challenges
from CTFd.models import db, Challenges, Files, Solves, WrongKeys, Keys

import time
import re
import logging

def init_challenges(app):
    @app.route('/challenges', methods=['GET'])
    def challenges():
        if not ctftime():
            return redirect('/')
        if can_view_challenges():
            return render_template('chals.html')
        else:
            return redirect(url_for('login', next="challenges"))

    @app.route('/chals', methods=['GET'])
    def chals():
        if not ctftime():
            return redirect('/')
        if can_view_challenges():
            chals = Challenges.query.add_columns('id', 'name', 'value', 'description', 'category').order_by(Challenges.value).all()
            
            json = {'game':[]}
            for x in chals:
                files = [ str(f.location) for f in Files.query.filter_by(chal=x.id).all() ]
                json['game'].append({'id':x[1], 'name':x[2], 'value':x[3], 'description':x[4], 'category':x[5], 'files':files})

            db.session.close()
            return jsonify(json)
        else:
            db.session.close()
            return redirect('/login')

    @app.route('/chals/solves')
    def chals_per_solves():
        if can_view_challenges():
            solves = Solves.query.add_columns(db.func.count(Solves.chalid)).group_by(Solves.chalid).all()
            json = {}        
            for chal, count in solves:
                json[chal.chal.name] = count
            return jsonify(json)
        return redirect(url_for('login', next="/chals/solves"))

    @app.route('/solves')
    @app.route('/solves/<teamid>')
    def solves(teamid=None):
        if teamid is None:
            if authed():
                solves = Solves.query.filter_by(teamid=session['id']).all()
            else:
                abort(401)
        else:
            solves = Solves.query.filter_by(teamid=teamid).all()
        db.session.close()
        json = {'solves':[]}
        for x in solves:
            json['solves'].append({'id':x.id, 'chal':x.chal.name, 'chalid':x.chalid,'team':x.teamid, 'value': x.chal.value, 'category':x.chal.category, 'time':unix_time(x.date)})
        return jsonify(json)

    @app.route('/fails/<teamid>', methods=['GET'])
    def fails(teamid):
        fails = WrongKeys.query.filter_by(team=teamid).count()
        solves = Solves.query.filter_by(teamid=teamid).count()
        db.session.close()
        json = {'fails':str(fails), 'solves': str(solves)}
        return jsonify(json)

    @app.route('/chal/<chalid>/solves', methods=['GET'])
    def who_solved(chalid):
        solves = Solves.query.filter_by(chalid=chalid)
        json = {'teams':[]}
        for solve in solves:
            json['teams'].append({'id':solve.team.id, 'name':solve.team.name, 'date':solve.date})
        return jsonify(json)

    @app.route('/chal/<chalid>', methods=['POST'])
    def chal(chalid):
        if not ctftime():
            return redirect('/')
        if authed():
            logger = logging.getLogger('keys')
            data = (time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8'), request.form['key'].encode('utf-8'), get_kpm(session['id']))
            print "[{0}] {1} submitted {2} with kpm {3}".format(*data)
            if get_kpm(session['id']) > 10:
                wrong = WrongKeys(session['id'], chalid, request.form['key'])
                db.session.add(wrong)
                db.session.commit()
                db.session.close()
                logger.warn("[{0}] {1} submitted {2} with kpm {3} [TOO FAST]".format(*data))
                return "3" # Submitting too fast
            solves = Solves.query.filter_by(teamid=session['id'], chalid=chalid).first()
            if not solves:
                keys = Keys.query.filter_by(chal=chalid).all()
                key = request.form['key'].strip().lower()
                for x in keys:
                    if x.key_type == 0: #static key
                        if x.flag.strip().lower() == key:
                            solve = Solves(chalid=chalid, teamid=session['id'], ip=request.remote_addr)
                            db.session.add(solve)
                            db.session.commit()
                            db.session.close()
                            logger.info("[{0}] {1} submitted {2} with kpm {3} [CORRECT]".format(*data))
                            return "1" # key was correct
                    elif x.key_type == 1: #regex 
                        res = re.match(str(x), key, re.IGNORECASE)
                        if res and res.group() == key:
                            solve = Solves(chalid=chalid, teamid=session['id'], ip=request.remote_addr)
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
            else:
                logger.info("{0} submitted {1} with kpm {2} [ALREADY SOLVED]".format(*data))
                return "2" # challenge was already solved
        else:
            return "-1"
