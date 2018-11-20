from flask import current_app as app, render_template, request, redirect, jsonify, render_template_string
from CTFd.utils.decorators import admins_only
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs, Hints, Unlocks
from CTFd.plugins.flags import get_flag_class, FLAG_CLASSES
from CTFd.plugins.challenges import get_chal_class, CHALLENGE_CLASSES
from CTFd.admin import admin
from CTFd.utils import config, validators, uploads
import os


@admin.route('/admin/challenges')
@admins_only
def challenges_listing():
    challenges = Challenges.query.all()
    return render_template('admin/challenges/challenges.html', challenges=challenges)


@admin.route('/admin/challenges/<int:challenge_id>')
@admins_only
def challenges_detail(challenge_id):
    challenges = dict(Challenges.query.with_entities(Challenges.id, Challenges.name).all())
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    solves = Solves.query.filter_by(challenge_id=challenge.id).all()
    flags = Flags.query.filter_by(challenge_id=challenge.id).all()
    challenge_class = get_chal_class(challenge.type)

    static_path = os.path.basename(challenge_class.blueprint.static_url_path)
    update_j2 = render_template_string(
        challenge_class.blueprint.open_resource(
            os.path.join(static_path, 'update.html')
        ).read().decode('utf-8'),
        # Python 3
        challenge=challenge
    )
    update_script = os.path.join(challenge_class.route, 'update.js')
    return render_template(
        'admin/challenges/challenge.html',
        update_template=update_j2,
        update_script=update_script,
        challenge=challenge,
        challenges=challenges,
        solves=solves,
        flags=flags
    )


@admin.route('/admin/challenges/new')
@admins_only
def challenges_new():
    return render_template('admin/challenges/new.html')
