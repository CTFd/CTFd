from flask import render_template, request

from CTFd.admin import admin
from CTFd.models import Pages
from CTFd.schemas.pages import PageSchema
from CTFd.utils import markdown
from CTFd.utils.config.pages import build_html
from CTFd.utils.decorators import admins_only


@admin.route("/admin/pages")
@admins_only
def pages_listing():
    pages = Pages.query.all()
    return render_template("admin/pages.html", pages=pages)


@admin.route("/admin/pages/new")
@admins_only
def pages_new():
    return render_template("admin/editor.html")


@admin.route("/admin/pages/preview", methods=["POST"])
@admins_only
def pages_preview():
    # We only care about content.
    # Loading other attributes improperly will cause Marshmallow to incorrectly return a dict
    data = {"content": request.form.get("content")}
    schema = PageSchema()
    page = schema.load(data)
    return render_template("page.html", content=build_html(page.data.content))


@admin.route("/admin/pages/<int:page_id>")
@admins_only
def pages_detail(page_id):
    page = Pages.query.filter_by(id=page_id).first_or_404()
    page_op = request.args.get("operation")

    if request.method == "GET" and page_op == "preview":
        return render_template("page.html", content=markdown(page.content))

    if request.method == "GET" and page_op == "create":
        return render_template("admin/editor.html")

    return render_template("admin/editor.html", page=page)
