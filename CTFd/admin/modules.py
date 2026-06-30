from flask import render_template, request
from sqlalchemy import or_

from CTFd.admin import admin
from CTFd.models import Audiences, Challenges, ModuleAudienceAccess, Modules
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
    linked_audiences = (
        Audiences.query.join(
            ModuleAudienceAccess, ModuleAudienceAccess.audience_id == Audiences.id
        )
        .filter(ModuleAudienceAccess.module_id == module_id)
        .all()
    )
    linked_audience_ids = {c.id for c in linked_audiences}
    all_audiences = Audiences.query.order_by(Audiences.name.asc()).all()
    challenges = (
        Challenges.query.filter_by(module_id=module_id)
        .order_by(Challenges.id.asc())
        .all()
    )
    # Candidate challenges to add: not in this module (either ungrouped or assigned elsewhere).
    addable_challenges = (
        Challenges.query.filter(
            or_(Challenges.module_id.is_(None), Challenges.module_id != module_id)
        )
        .order_by(Challenges.category.asc(), Challenges.name.asc())
        .all()
    )
    return render_template(
        "admin/modules/module.html",
        module=module,
        linked_audiences=linked_audiences,
        linked_audience_ids=linked_audience_ids,
        all_audiences=all_audiences,
        challenges=challenges,
        addable_challenges=addable_challenges,
    )
