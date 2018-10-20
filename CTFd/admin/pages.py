from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs
from CTFd.schemas.pages import PageSchema
from CTFd.utils import config, validators, markdown, uploads
from CTFd.cache import cache
from CTFd.admin import admin


@admin.route('/admin/pages', methods=['GET', 'POST'])
@admins_only
def admin_pages_list():
    pages = Pages.query.all()
    return render_template('admin/pages.html', pages=pages)


@admin.route('/admin/pages/new', methods=['GET', 'POST'])
@admins_only
def admin_pages_new():
    return render_template('admin/editor.html')


@admin.route('/admin/pages/preview', methods=['POST'])
@admins_only
def admin_pages_preview():
    data = request.form.to_dict()
    schema = PageSchema()
    page = schema.load(data)
    return render_template('page.html', content=markdown(page.data.content))


@admin.route('/admin/pages/<int:page_id>', methods=['GET', 'POST'])
@admins_only
def admin_pages_detail(page_id):
    page = Pages.query.filter_by(id=page_id).first_or_404()
    page_op = request.args.get('operation')

    if request.method == 'GET' and page_op == 'preview':
        return render_template('page.html', content=markdown(page.content))

    if request.method == 'GET' and page_op == 'create':
        return render_template('admin/editor.html')

    return render_template('admin/editor.html', page=page)