from flask import render_template, request
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from CTFd.admin import admin
from CTFd.models import (
    AudienceMembers,
    Audiences,
    Challenges,
    ModuleAudienceAccess,
    Modules,
    db,
)
from CTFd.utils.decorators import admins_only


@admin.route("/admin/modules")
@admins_only
def modules_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []
    if q and field and Modules.__mapper__.has_property(field):
        filters.append(getattr(Modules, field).like("%{}%".format(q)))

    modules = Modules.query.filter(*filters).order_by(Modules.id.asc()).all()
    return render_template(
        "admin/modules/modules.html", modules=modules, q=q, field=field
    )


@admin.route("/admin/modules/new")
@admins_only
def modules_new():
    return render_template("admin/modules/new.html")


@admin.route("/admin/modules/<int:module_id>")
@admins_only
def modules_detail(module_id):
    module = Modules.query.filter_by(id=module_id).first_or_404()

    audiences = Audiences.query.order_by(Audiences.name.asc()).all()
    member_counts = dict(
        db.session.query(AudienceMembers.audience_id, func.count(AudienceMembers.id))
        .group_by(AudienceMembers.audience_id)
        .all()
    )
    linked_audience_ids = {
        link.audience_id
        for link in ModuleAudienceAccess.query.filter_by(module_id=module_id)
    }

    challenges = (
        Challenges.query.options(selectinload(Challenges.modules))
        .order_by(Challenges.category.asc(), Challenges.name.asc())
        .all()
    )
    linked_challenge_ids = {c.id for c in challenges if module_id in c.module_ids}
    challenges.sort(key=lambda c: c.id not in linked_challenge_ids)

    return render_template(
        "admin/modules/module.html",
        module=module,
        audiences=audiences,
        member_counts=member_counts,
        linked_audience_ids=linked_audience_ids,
        challenges=challenges,
        linked_challenge_ids=linked_challenge_ids,
    )
