from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.models import db, Teams, Solves, Challenges, Fails, Submissions
from passlib.hash import bcrypt_sha256
from sqlalchemy.sql import not_

from CTFd import utils
from CTFd.admin import admin


@admin.route('/admin/submissions', defaults={'submission_type': None})
@admin.route('/admin/submissions/<submission_type>')
@admins_only
def list_submissions(submission_type):
    filters = {}
    if submission_type:
        filters['type'] = submission_type

    curr_page = abs(int(request.args.get('page', 1)))
    results_per_page = 50
    page_start = results_per_page * (curr_page - 1)
    page_end = results_per_page * (curr_page - 1) + results_per_page
    sub_count = Submissions.query.filter_by(**filters).count()
    page_count = int(sub_count / results_per_page) + (sub_count % results_per_page > 0)

    submissions = Submissions.query.add_columns(
        Submissions.id,
        Submissions.challenge_id,
        Submissions.provided,
        Submissions.team_id,
        Submissions.date,
        Challenges.name.label('challenge_name'),
        Teams.name.label('team_name')
    )\
        .filter_by(**filters) \
        .join(Challenges)\
        .join(Teams)\
        .order_by(Fails.date.desc())\
        .slice(page_start, page_end)\
        .all()

    return render_template(
        'admin/submissions.html',
        submissions=submissions,
        page_count=page_count,
        curr_page=curr_page,
        type=submission_type
    )