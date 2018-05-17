from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, Hints, Unlocks, DatabaseError
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
        challenge_class = CHALLENGE_CLASSES.get(class_id)
        data[challenge_class.id] = {
            'id': challenge_class.id,
            'name': challenge_class.name,
            'templates': challenge_class.templates,
            'scripts': challenge_class.scripts,
        }

    return jsonify(data)


@admin_challenges.route('/admin/chals', methods=['POST', 'GET'])
@admins_only
def admin_chals():
    if request.method == 'POST':
        chals = Challenges.query.order_by(Challenges.value).all()

        json_data = {'game': []}
        for chal in chals:
            tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal.id).all()]
            files = [str(f.location) for f in Files.query.filter_by(chal=chal.id).all()]
            hints = []
            for hint in Hints.query.filter_by(chal=chal.id).all():
                hints.append({'id': hint.id, 'cost': hint.cost, 'hint': hint.hint})

            type_class = CHALLENGE_CLASSES.get(chal.type)
            type_name = type_class.name if type_class else None

            json_data['game'].append({
                'id': chal.id,
                'name': chal.name,
                'value': chal.value,
                'description': chal.description,
                'category': chal.category,
                'files': files,
                'tags': tags,
                'hints': hints,
                'hidden': chal.hidden,
                'max_attempts': chal.max_attempts,
                'type': chal.type,
                'type_name': type_name,
                'type_data': {
                    'id': type_class.id,
                    'name': type_class.name,
                    'templates': type_class.templates,
                    'scripts': type_class.scripts,
                }
            })

        db.session.close()
        return jsonify(json_data)
    else:
        challenges = Challenges.query.all()
        return render_template('admin/challenges.html', challenges=challenges)


@admin_challenges.route('/admin/chal/<int:chalid>', methods=['GET', 'POST'])
@admins_only
def admin_chal_detail(chalid):
    chal = Challenges.query.filter_by(id=chalid).first_or_404()
    chal_class = get_chal_class(chal.type)

    if request.method == 'POST':
        status, message = chal_class.attempt(chal, request)
        if status:
            return jsonify({'status': 1, 'message': message})
        else:
            return jsonify({'status': 0, 'message': message})
    elif request.method == 'GET':
        obj, data = chal_class.read(chal)

        tags = [tag.tag for tag in Tags.query.add_columns('tag').filter_by(chal=chal.id).all()]
        files = [str(f.location) for f in Files.query.filter_by(chal=chal.id).all()]
        hints = []
        for hint in Hints.query.filter_by(chal=chal.id).all():
            hints.append({'id': hint.id, 'cost': hint.cost, 'hint': hint.hint})

        data['tags'] = tags
        data['files'] = files
        data['hints'] = hints

        return jsonify(data)


@admin_challenges.route('/admin/chal/<int:chalid>/solves', methods=['GET'])
@admins_only
def admin_chal_solves(chalid):
    response = {'teams': []}
    if utils.hide_scores():
        return jsonify(response)
    solves = Solves.query.join(Teams, Solves.teamid == Teams.id).filter(Solves.chalid == chalid).order_by(
        Solves.date.asc())
    for solve in solves:
        response['teams'].append({'id': solve.team.id, 'name': solve.team.name, 'date': solve.date})
    return jsonify(response)


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
            hint.cost = int(request.form.get('cost') or 0)
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
            cost = int(request.form.get('cost') or 0)
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
            key_class = get_key_class(x.type)
            json_data['keys'].append({
                'id': x.id,
                'key': x.flag,
                'type': x.type,
                'type_name': key_class.name,
                'templates': key_class.templates,
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
        chal_type = request.form['chaltype']
        chal_class = get_chal_class(chal_type)
        chal_class.create(request)
        return redirect(url_for('admin_challenges.admin_chals'))
    else:
        return render_template('admin/chals/create.html')


@admin_challenges.route('/admin/chal/delete', methods=['POST'])
@admins_only
def admin_delete_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first_or_404()
    chal_class = get_chal_class(challenge.type)
    chal_class.delete(challenge)
    return '1'


@admin_challenges.route('/admin/chal/update', methods=['POST'])
@admins_only
def admin_update_chal():
    challenge = Challenges.query.filter_by(id=request.form['id']).first_or_404()
    chal_class = get_chal_class(challenge.type)
    chal_class.update(challenge, request)
    return redirect(url_for('admin_challenges.admin_chals'))
