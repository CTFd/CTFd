from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache
from CTFd.models import db, Teams, Solves, Awards, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, Hints, Unlocks, DatabaseError
from CTFd.plugins.keys import get_key_class, KEY_CLASSES
from CTFd.plugins.challenges import get_chal_class, CHALLENGE_CLASSES

from CTFd import utils

import os

admin_challenges = Blueprint('admin_challenges', __name__)


@admin_challenges.route('/admin/chal_types', methods=['GET'])
@admins_only
def admin_chal_types():
    data = {}
    for class_id in CHALLENGE_CLASSES:
        data[class_id] = CHALLENGE_CLASSES.get(class_id).name

    return jsonify(data)


@admin_challenges.route('/admin/chals', methods=['POST', 'GET'])
@admins_only
def admin_chals():
    if request.method == 'POST':
        chals = Challenges.query.add_columns('id', 'type', 'name', 'value', 'description', 'category', 'hidden', 'max_attempts').order_by(Challenges.value).all()

        teams_with_points = db.session.query(Solves.teamid).join(Teams).filter(
            Teams.banned == False).group_by(Solves.teamid).count()

        json_data = {'game': []}
        for x in chals:
            solve_count = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(
                Solves.chalid == x[1], Teams.banned == False).count()
            if teams_with_points > 0:
                percentage = (float(solve_count) / float(teams_with_points))
            else:
                percentage = 0.0

            type_class = CHALLENGE_CLASSES.get(x.type)
            type_name = type_class.name if type_class else None

            json_data['game'].append({
                'id': x.id,
                'name': x.name,
                'value': x.value,
                'description': x.description,
                'category': x.category,
                'hidden': x.hidden,
                'max_attempts': x.max_attempts,
                'type': x.type,
                'type_name': type_name,
                'percentage_solved': percentage
            })

        db.session.close()
        return jsonify(json_data)
    else:
        return render_template('admin/chals.html')


@admin_challenges.route('/admin/tags/<int:chalid>', methods=['GET', 'POST'])
@admins_only
def admin_tags(chalid):
    if request.method == 'GET':
        tags = Tags.query.filter_by(chal=chalid).all()
        json_data = {'tags': []}
        for x in tags:
            json_data['tags'].append({'id': x.id, 'chal': x.chal, 'tag': x.tag})
        return jsonify(json_data)

    elif request.method == 'POST':
        newtags = request.form.getlist('tags[]')
        for x in newtags:
            tag = Tags(chalid, x)
            db.session.add(tag)
        db.session.commit()
        db.session.close()
        return '1'


@admin_challenges.route('/admin/tags/<int:tagid>/delete', methods=['POST'])
@admins_only
def admin_delete_tags(tagid):
    if request.method == 'POST':
        tag = Tags.query.filter_by(id=tagid).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()
        return '1'


@admin_challenges.route('/admin/hints', defaults={'hintid': None}, methods=['POST', 'GET'])
@admin_challenges.route('/admin/hints/<int:hintid>', methods=['GET', 'POST', 'DELETE'])
@admins_only
def admin_hints(hintid):
    if hintid:
        hint = Hints.query.filter_by(id=hintid).first_or_404()

        if request.method == 'POST':
            hint.hint = request.form.get('hint')
            hint.chal = int(request.form.get('chal'))
            hint.cost = int(request.form.get('cost'))
            db.session.commit()

        elif request.method == 'DELETE':
            db.session.delete(hint)
            db.session.commit()
            db.session.close()
            return ('', 204)

        json_data = {
            'hint': hint.hint,
            'type': hint.type,
            'chal': hint.chal,
            'cost': hint.cost,
            'id': hint.id
        }
        db.session.close()
        return jsonify(json_data)
    else:
        if request.method == 'GET':
            hints = Hints.query.all()
            json_data = []
            for hint in hints:
                json_data.append({
                    'hint': hint.hint,
                    'type': hint.type,
                    'chal': hint.chal,
                    'cost': hint.cost,
                    'id': hint.id
                })
            return jsonify({'results': json_data})
        elif request.method == 'POST':
            hint = request.form.get('hint')
            chalid = int(request.form.get('chal'))
            cost = int(request.form.get('cost'))
            hint_type = request.form.get('type', 0)
            hint = Hints(chal=chalid, hint=hint, cost=cost)
            db.session.add(hint)
            db.session.commit()
            json_data = {
                'hint': hint.hint,
                'type': hint.type,
                'chal': hint.chal,
                'cost': hint.cost,
                'id': hint.id
            }
            db.session.close()
            return jsonify(json_data)


@admin_challenges.route('/admin/files/<int:chalid>', methods=['GET', 'POST'])
@admins_only
def admin_files(chalid):
    if request.method == 'GET':
        files = Files.query.filter_by(chal=chalid).all()
        json_data = {'files': []}
        for x in files:
            json_data['files'].append({'id': x.id, 'file': x.location})
        return jsonify(json_data)
    if request.method == 'POST':
        if request.form['method'] == "delete":
            utils.delete_file(request.form['file'])

            db.session.commit()
            db.session.close()
            return '1'
        elif request.form['method'] == "upload":
            files = request.files.getlist('files[]')

            for f in files:
                utils.upload_file(file=f, chalid=chalid)

            db.session.commit()
            db.session.close()
            return '1'


@admin_challenges.route('/admin/chal/<int:chalid>/<prop>', methods=['GET'])
@admins_only
def admin_get_values(chalid, prop):
    challenge = Challenges.query.filter_by(id=chalid).first_or_404()
    if prop == 'keys':
        chal_keys = Keys.query.filter_by(chal=challenge.id).all()
        json_data = {'keys': []}
        for x in chal_keys:
            json_data['keys'].append({
                'id': x.id,
                'key': x.flag,
                'type': x.key_type,
                'type_name': get_key_class(x.key_type).name
            })
        return jsonify(json_data)
    elif prop == 'tags':
        tags = Tags.query.filter_by(chal=chalid).all()
        json_data = {'tags': []}
        for x in tags:
            json_data['tags'].append({
                'id': x.id,
                'chal': x.chal,
                'tag': x.tag
            })
        return jsonify(json_data)
    elif prop == 'hints':
        hints = Hints.query.filter_by(chal=chalid)
        json_data = {'hints': []}
        for hint in hints:
            json_data['hints'].append({
                'hint': hint.hint,
                'type': hint.type,
                'chal': hint.chal,
                'cost': hint.cost,
                'id': hint.id
            })
        return jsonify(json_data)


@admin_challenges.route('/admin/chal/new', methods=['GET', 'POST'])
@admins_only
def admin_create_chal():
    if request.method == 'POST':
        files = request.files.getlist('files[]')

        # Create challenge
        chal = Challenges(request.form['name'], request.form['desc'], request.form['value'], request.form['category'], int(request.form['chaltype']))
        if 'hidden' in request.form:
            chal.hidden = True
        else:
            chal.hidden = False

        max_attempts = request.form.get('max_attempts')
        if max_attempts and max_attempts.isdigit():
            chal.max_attempts = int(max_attempts)

        db.session.add(chal)
        db.session.flush()

        flag = Keys(chal.id, request.form['key'], int(request.form['key_type[0]']))
        if request.form.get('keydata'):
            flag.data = request.form.get('keydata')
        db.session.add(flag)

        db.session.commit()

        for f in files:
            utils.upload_file(file=f, chalid=chal.id)

        db.session.commit()
        db.session.close()
        return redirect(url_for('admin_challenges.admin_chals'))
    else:
        return render_template('admin/chals/create.html')


@admin_challenges.route('/admin/chal/delete', methods=['POST'])
@admins_only
def admin_delete_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first_or_404()
    WrongKeys.query.filter_by(chalid=challenge.id).delete()
    Solves.query.filter_by(chalid=challenge.id).delete()
    Keys.query.filter_by(chal=challenge.id).delete()
    files = Files.query.filter_by(chal=challenge.id).all()
    for f in files:
        utils.delete_file(f.id)
    Files.query.filter_by(chal=challenge.id).delete()
    Tags.query.filter_by(chal=challenge.id).delete()
    Challenges.query.filter_by(id=challenge.id).delete()
    db.session.commit()
    db.session.close()
    return '1'


@admin_challenges.route('/admin/chal/update', methods=['POST'])
@admins_only
def admin_update_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first_or_404()
    challenge.name = request.form['name']
    challenge.description = request.form['desc']
    challenge.value = int(request.form.get('value', 0)) if request.form.get('value', 0) else 0
    challenge.max_attempts = int(request.form.get('max_attempts', 0)) if request.form.get('max_attempts', 0) else 0
    challenge.category = request.form['category']
    challenge.hidden = 'hidden' in request.form
    db.session.add(challenge)
    db.session.commit()
    db.session.close()
    return redirect(url_for('admin_challenges.admin_chals'))
