from flask import render_template, request
from CTFd.utils.decorators import admins_only
from CTFd.models import Challenges, Submissions
from CTFd.utils.modes import get_model
from CTFd.admin import admin


@admin.route("/admin/submissions", defaults={"submission_type": None})
@admin.route("/admin/submissions/<submission_type>")
@admins_only
def submissions_listing(submission_type):
    filters = {}
    if submission_type:
        filters["type"] = submission_type

    curr_page = abs(int(request.args.get("page", 1, type=int)))
    results_per_page = 50
    page_start = results_per_page * (curr_page - 1)
    page_end = results_per_page * (curr_page - 1) + results_per_page
    sub_count = Submissions.query.filter_by(**filters).count()
    page_count = int(sub_count / results_per_page) + (sub_count % results_per_page > 0)

    Model = get_model()

    submissions = (
        Submissions.query.add_columns(
            Submissions.id,
            Submissions.type,
            Submissions.challenge_id,
            Submissions.provided,
            Submissions.account_id,
            Submissions.date,
            Challenges.name.label("challenge_name"),
            Model.name.label("team_name"),
        )
        .filter_by(**filters)
        .join(Challenges)
        .join(Model)
        .order_by(Submissions.date.desc())
        .slice(page_start, page_end)
        .all()
    )

    return render_template(
        "admin/submissions.html",
        submissions=submissions,
        page_count=page_count,
        curr_page=curr_page,
        type=submission_type,
    )
