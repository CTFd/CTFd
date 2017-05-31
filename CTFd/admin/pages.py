from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache
from CTFd.models import db, Teams, Solves, Awards, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError

from CTFd import utils

admin_pages = Blueprint('admin_pages', __name__)


@admin_pages.route('/admin/css', methods=['GET', 'POST'])
@admins_only
def admin_css():
    if request.method == 'POST':
        css = request.form['css']
        css = utils.set_config('css', css)
        with app.app_context():
            cache.clear()
        return '1'
    return '0'


@admin_pages.route('/admin/pages', defaults={'route': None}, methods=['GET', 'POST'])
@admin_pages.route('/admin/pages/<route>', methods=['GET', 'POST'])
@admins_only
def admin_pages_view(route):
    if request.method == 'GET' and request.args.get('mode') == 'create':
        return render_template('admin/editor.html')
    if route and request.method == 'GET':
        page = Pages.query.filter_by(route=route).first()
        return render_template('admin/editor.html', page=page)
    if route and request.method == 'POST':
        page = Pages.query.filter_by(route=route).first()
        errors = []
        html = request.form['html']
        route = request.form['route']
        if not route:
            errors.append('Missing URL route')
        if errors:
            page = Pages(html, '')
            return render_template('/admin/editor.html', page=page)
        if page:
            page.route = route
            page.html = html
            db.session.commit()
            db.session.close()
            return redirect(url_for('admin_pages.admin_pages_view'))
        page = Pages(route, html)
        db.session.add(page)
        db.session.commit()
        db.session.close()
        return redirect(url_for('admin_pages.admin_pages_view'))
    pages = Pages.query.all()
    return render_template('admin/pages.html', routes=pages, css=utils.get_config('css'))


@admin_pages.route('/admin/media', methods=['GET', 'POST', 'DELETE'])
@admins_only
def admin_pages_media():
    if request.method == 'POST':
        files = request.files.getlist('files[]')

        uploaded = []
        for f in files:
            data = utils.upload_file(file=f, chalid=None)
            if data:
                uploaded.append({'id': data[0], 'location': data[1]})
        return jsonify({'results': uploaded})
    elif request.method == 'DELETE':
        file_ids = request.form.getlist('file_ids[]')
        for file_id in file_ids:
            utils.delete_file(file_id)
        return True
    else:
        files = [{'id': f.id, 'location': f.location} for f in Files.query.filter_by(chal=None).all()]
        return jsonify({'results': files})


@admin_pages.route('/admin/page/<pageroute>/delete', methods=['POST'])
@admins_only
def delete_page(pageroute):
    page = Pages.query.filter_by(route=pageroute).first_or_404()
    db.session.delete(page)
    db.session.commit()
    db.session.close()
    return '1'
