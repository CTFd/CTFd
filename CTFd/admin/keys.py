from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError
from CTFd.plugins.keys import get_key_class, KEY_CLASSES

from CTFd import utils

admin_keys = Blueprint('admin_keys', __name__)


@admin_keys.route('/admin/key_types', methods=['GET'])
@admin_keys.route('/admin/key_types/<key_id>', methods=['GET'])
@admins_only
def admin_key_types(key_id=None):
    if key_id is None:
        data = {}
        for class_id in KEY_CLASSES:
            data[class_id] = KEY_CLASSES.get(class_id).name

        return jsonify(data)
    else:
        key_class = get_key_class(key_id)
        data = {
            'id': key_class.id,
            'name': key_class.name,
            'templates': key_class.templates
        }
        return jsonify(data)


@admin_keys.route('/admin/keys', defaults={'keyid': None}, methods=['POST', 'GET'])
@admin_keys.route('/admin/keys/<int:keyid>', methods=['POST', 'GET'])
@admins_only
def admin_keys_view(keyid):
    if request.method == 'GET':
        if keyid:
            saved_key = Keys.query.filter_by(id=keyid).first_or_404()
            key_class = get_key_class(saved_key.type)
            json_data = {
                'id': saved_key.id,
                'key': saved_key.flag,
                'data': saved_key.data,
                'chal': saved_key.chal,
                'type': saved_key.type,
                'type_name': key_class.name,
                'templates': key_class.templates,
            }

            return jsonify(json_data)
    elif request.method == 'POST':
        chal = request.form.get('chal')
        flag = request.form.get('key')
        data = request.form.get('keydata')
        key_type = request.form.get('key_type')
        if not keyid:
            k = Keys(chal, flag, key_type)
            k.data = data
            db.session.add(k)
        else:
            k = Keys.query.filter_by(id=keyid).first()
            k.flag = flag
            k.data = data
            k.type = key_type
        db.session.commit()
        db.session.close()
        return '1'


@admin_keys.route('/admin/keys/<int:keyid>/delete', methods=['POST'])
@admins_only
def admin_delete_keys(keyid):
    if request.method == 'POST':
        key = Keys.query.filter_by(id=keyid).first_or_404()
        db.session.delete(key)
        db.session.commit()
        db.session.close()
        return '1'
