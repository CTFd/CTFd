from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils import admins_only, is_admin, unix_time, get_config, \
    set_config, sendmail, rmdir, create_image, delete_image, run_image, container_status, container_ports, \
    container_stop, container_start, get_themes, cache, upload_file
from CTFd.models import db, Teams, Solves, Awards, Containers, Challenges, WrongKeys, Keys, Tags, Files, Tracking, Pages, Config, DatabaseError

admin_containers = Blueprint('admin_containers', __name__)

@admin_containers.route('/admin/containers', methods=['GET'])
@admins_only
def list_container():
    containers = Containers.query.all()
    for c in containers:
        c.status = container_status(c.name)
        c.ports = ', '.join(container_ports(c.name, verbose=True))
    return render_template('admin/containers.html', containers=containers)


@admin_containers.route('/admin/containers/<int:container_id>/stop', methods=['POST'])
@admins_only
def stop_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if container_stop(container.name):
        return '1'
    else:
        return '0'


@admin_containers.route('/admin/containers/<int:container_id>/start', methods=['POST'])
@admins_only
def run_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if container_status(container.name) == 'missing':
        if run_image(container.name):
            return '1'
        else:
            return '0'
    else:
        if container_start(container.name):
            return '1'
        else:
            return '0'


@admin_containers.route('/admin/containers/<int:container_id>/delete', methods=['POST'])
@admins_only
def delete_container(container_id):
    container = Containers.query.filter_by(id=container_id).first_or_404()
    if delete_image(container.name):
        db.session.delete(container)
        db.session.commit()
        db.session.close()
    return '1'


@admin_containers.route('/admin/containers/new', methods=['POST'])
@admins_only
def new_container():
    name = request.form.get('name')
    if not set(name) <= set('abcdefghijklmnopqrstuvwxyz0123456789-_'):
        return redirect(url_for('admin_containers.list_container'))
    buildfile = request.form.get('buildfile')
    files = request.files.getlist('files[]')
    create_image(name=name, buildfile=buildfile, files=files)
    run_image(name)
    return redirect(url_for('admin_containers.list_container'))