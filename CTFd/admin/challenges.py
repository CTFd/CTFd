from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs, Hints, Unlocks
from CTFd.plugins.flags import get_flag_class, FLAG_CLASSES
from CTFd.plugins.challenges import get_chal_class, CHALLENGE_CLASSES
from CTFd.admin import admin
from CTFd.utils import config, validators, uploads


@admin.route('/admin/challenges', methods=['POST', 'GET'])
@admins_only
def admin_chals():
    challenges = Challenges.query.all()
    return render_template('admin/challenges.html', challenges=challenges)


@admin.route('/admin/files/<int:chalid>', methods=['GET', 'POST'])
@admins_only
def admin_files(chalid):
    # TODO: Potentially move to API?
    if request.method == 'GET':
        files = Files.query.filter_by(chal=chalid).all()
        json_data = {'files': []}
        for x in files:
            json_data['files'].append({'id': x.id, 'file': x.location})
        return jsonify(json_data)
    if request.method == 'POST':
        if request.form['method'] == "delete":
            uploads.delete_file(request.form['file'])

            db.session.commit()
            db.session.close()
            return '1'
        elif request.form['method'] == "upload":
            files = request.files.getlist('files[]')

            for f in files:
                uploads.upload_file(file=f, chalid=chalid)

            db.session.commit()
            db.session.close()
            return '1'


@admin.route('/admin/challenges/new', methods=['GET', 'POST'])
@admins_only
def admin_create_chal():
    # TODO: Move to API
    if request.method == 'POST':
        chal_type = request.form['chaltype']
        chal_class = get_chal_class(chal_type)
        chal_class.create(request)
        return redirect(url_for('admin.admin_chals'))
    else:
        return render_template('admin/chals/create.html')

