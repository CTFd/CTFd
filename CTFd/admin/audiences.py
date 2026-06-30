from flask import render_template, request
from sqlalchemy.orm import joinedload

from CTFd.admin import admin
from CTFd.models import AudienceMembers, Audiences, ModuleAudienceAccess, Modules
from CTFd.utils import config as ctf_config
from CTFd.utils.decorators import admins_only


@admin.route("/admin/audiences")
@admins_only
def audiences_listing():
    q = request.args.get("q")
    field = request.args.get("field")
    filters = []
    if q and field and Audiences.__mapper__.has_property(field):
        filters.append(getattr(Audiences, field).like("%{}%".format(q)))

    audiences = Audiences.query.filter(*filters).order_by(Audiences.id.asc()).all()
    return render_template(
        "admin/audiences/audiences.html", audiences=audiences, q=q, field=field
    )


@admin.route("/admin/audiences/new")
@admins_only
def audiences_new():
    return render_template("admin/audiences/new.html")


@admin.route("/admin/audiences/<int:audience_id>")
@admins_only
def audiences_detail(audience_id):
    audience = Audiences.query.filter_by(id=audience_id).first_or_404()
    members = (
        AudienceMembers.query.filter_by(audience_id=audience_id)
        .options(joinedload(AudienceMembers.user), joinedload(AudienceMembers.team))
        .all()
    )
    linked_modules = (
        Modules.query.join(
            ModuleAudienceAccess, ModuleAudienceAccess.module_id == Modules.id
        )
        .filter(ModuleAudienceAccess.audience_id == audience_id)
        .all()
    )
    # All modules, for the link-picker (annotate which are already linked)
    linked_module_ids = {m.id for m in linked_modules}
    all_modules = Modules.query.order_by(Modules.name.asc()).all()
    return render_template(
        "admin/audiences/audience.html",
        audience=audience,
        members=members,
        linked_modules=linked_modules,
        linked_module_ids=linked_module_ids,
        all_modules=all_modules,
        user_mode=ctf_config.user_mode(),
    )
