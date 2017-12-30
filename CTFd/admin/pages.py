from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, cache, markdown
from CTFd.models import db, Teams, Solves, Awards, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError

from CTFd import utils

admin_pages = Blueprint('admin_pages', __name__)


@admin_pages.route('/admin/pages', methods=['GET', 'POST'])
@admins_only
def admin_pages_view():
    page_id = request.args.get('id')
    page_op = request.args.get('operation')

    if request.method == 'GET' and page_op == 'preview':
        page = Pages.query.filter_by(id=page_id).first_or_404()
        return render_template('page.html', content=markdown(page.html))

    if request.method == 'GET' and page_op == 'create':
        return render_template('admin/editor.html')

    if page_id and request.method == 'GET':
        page = Pages.query.filter_by(id=page_id).first()
        return render_template('admin/editor.html', page=page)

    if request.method == 'POST':
        page_form_id = request.form.get('id')
        title = request.form['title']
        html = request.form['html']
        route = request.form['route'].lstrip('/')
        auth_required = 'auth_required' in request.form

        if page_op == 'preview':
            page = Pages(title, route, html, draft=False)
            return render_template('page.html', content=markdown(page.html))

        page = Pages.query.filter_by(id=page_form_id).first()

        errors = []
        if not route:
            errors.append('Missing URL route')

        if errors:
            page = Pages(title, html, route)
            return render_template('/admin/editor.html', page=page)

        if page:
            page.title = title
            page.route = route
            page.html = html
            page.auth_required = auth_required

            if page_op == 'publish':
                page.draft = False

            db.session.commit()

            data = {
                'result': 'success',
                'operation': page_op,
                'page': {
                    'id': page.id,
                    'route': page.route,
                    'title': page.title
                }
            }

            db.session.close()
            cache.clear()
            return jsonify(data)

        if page_op == 'publish':
            page = Pages(title, route, html, draft=False, auth_required=auth_required)
        elif page_op == 'save':
            page = Pages(title, route, html, auth_required=auth_required)

        db.session.add(page)
        db.session.commit()

        data = {
            'result': 'success',
            'operation': page_op,
            'page': {
                'id': page.id,
                'route': page.route,
                'title': page.title
            }
        }

        db.session.close()
        cache.clear()

        return jsonify(data)

    pages = Pages.query.all()
    return render_template('admin/pages.html', pages=pages)


@admin_pages.route('/admin/pages/delete', methods=['POST'])
@admins_only
def delete_page():
    id = request.form['id']
    page = Pages.query.filter_by(id=id).first_or_404()
    db.session.delete(page)
    db.session.commit()
    db.session.close()
    with app.app_context():
        cache.clear()
    return '1'


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
