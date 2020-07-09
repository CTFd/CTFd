from flask import abort, render_template, request, url_for

from CTFd.admin import admin
from CTFd.models import Challenges, Flags, Solves
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.utils.decorators import admins_only


@admin.route("/admin/challenges")
@admins_only
def challenges_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []

    if q:
        # The field exists as an exposed column
        if Challenges.__mapper__.has_property(field):
            filters.append(getattr(Challenges, field).like("%{}%".format(q)))

    query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())
    challenges = query.all()
    total = query.count()

    return render_template(
        "admin/challenges/challenges.html",
        challenges=challenges,
        total=total,
        q=q,
        field=field,
    )


@admin.route("/admin/challenges/<int:challenge_id>")
@admins_only
def challenges_detail(challenge_id):
    challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
    )
    challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
    solves = (
        Solves.query.filter_by(challenge_id=challenge.id)
        .order_by(Solves.date.asc())
        .all()
    )
    flags = Flags.query.filter_by(challenge_id=challenge.id).all()

    try:
        challenge_class = get_chal_class(challenge.type)
    except KeyError:
        abort(
            500,
            f"The underlying challenge type ({challenge.type}) is not installed. This challenge can not be loaded.",
        )

    update_j2 = render_template(
        challenge_class.templates["update"].lstrip("/"), challenge=challenge
    )

    update_script = url_for(
        "views.static_html", route=challenge_class.scripts["update"].lstrip("/")
    )
    return render_template(
        "admin/challenges/challenge.html",
        update_template=update_j2,
        update_script=update_script,
        challenge=challenge,
        challenges=challenges,
        solves=solves,
        flags=flags,
    )


@admin.route("/admin/challenges/new")
@admins_only
def challenges_new():
    types = CHALLENGE_CLASSES.keys()
    return render_template("admin/challenges/new.html", types=types)
