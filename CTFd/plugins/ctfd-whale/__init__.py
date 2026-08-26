import fcntl
import warnings

import requests
from flask import Blueprint, render_template, session, current_app, request
from flask_apscheduler import APScheduler

from CTFd.api import CTFd_API_v1
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_admin_plugin_menu_bar,
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.utils import get_config, set_config
from CTFd.utils.decorators import admins_only

from .api import user_namespace, admin_namespace, AdminContainers
from .challenge_type import DynamicValueDockerChallenge
from .utils.checks import WhaleChecks
from .utils.control import ControlUtil
from .utils.db import DBContainer
from .utils.docker import DockerUtils
from .utils.exceptions import WhaleWarning
from .utils.setup import setup_default_configs
from .utils.routers import Router


def load(app):
    app.config['RESTX_ERROR_404_HELP'] = False
    # upgrade()
    plugin_name = __name__.split('.')[-1]
    set_config('whale:plugin_name', plugin_name)
    app.db.create_all()
    if not get_config("whale:setup"):
        setup_default_configs()

    register_plugin_assets_directory(
        app, base_path=f"/plugins/{plugin_name}/assets",
        endpoint='plugins.ctfd-whale.assets'
    )
    register_admin_plugin_menu_bar(
        title='Whale',
        route='/plugins/ctfd-whale/admin/settings'
    )

    DynamicValueDockerChallenge.templates = {
        "create": f"/plugins/{plugin_name}/assets/create.html",
        "update": f"/plugins/{plugin_name}/assets/update.html",
        "view": f"/plugins/{plugin_name}/assets/view.html",
    }
    DynamicValueDockerChallenge.scripts = {
        "create": "/plugins/ctfd-whale/assets/create.js",
        "update": "/plugins/ctfd-whale/assets/update.js",
        "view": "/plugins/ctfd-whale/assets/view.js",
    }
    CHALLENGE_CLASSES["dynamic_docker"] = DynamicValueDockerChallenge

    page_blueprint = Blueprint(
        "ctfd-whale",
        __name__,
        template_folder="templates",
        static_folder="assets",
        url_prefix="/plugins/ctfd-whale"
    )
    CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/ctfd-whale/admin")
    CTFd_API_v1.add_namespace(user_namespace, path="/plugins/ctfd-whale")

    worker_config_commit = None

    @page_blueprint.route('/admin/settings')
    @admins_only
    def admin_list_configs():
        nonlocal worker_config_commit
        errors = WhaleChecks.perform()
        if not errors and get_config("whale:refresh") != worker_config_commit:
            worker_config_commit = get_config("whale:refresh")
            DockerUtils.init()
            Router.reset()
            set_config("whale:refresh", "false")
        return render_template('whale_config.html', errors=errors)

    @page_blueprint.route("/admin/containers")
    @admins_only
    def admin_list_containers():
        result = AdminContainers.get()
        view_mode = request.args.get('mode', session.get('view_mode', 'list'))
        session['view_mode'] = view_mode
        return render_template("whale_containers.html",
                               plugin_name=plugin_name,
                               containers=result['data']['containers'],
                               pages=result['data']['pages'],
                               curr_page=abs(request.args.get("page", 1, type=int)),
                               curr_page_start=result['data']['page_start'])

    def auto_clean_container():
        with app.app_context():
            results = DBContainer.get_all_expired_container()
            for r in results:
                ControlUtil.try_remove_container(r.user_id)

    app.register_blueprint(page_blueprint)

    try:
        Router.check_availability()
        DockerUtils.init()
    except Exception:
        warnings.warn("Initialization Failed. Please check your configs.", WhaleWarning)

    try:
        lock_file = open("/tmp/ctfd_whale.lock", "w")
        lock_fd = lock_file.fileno()
        fcntl.lockf(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        scheduler.add_job(
            id='whale-auto-clean', func=auto_clean_container,
            trigger="interval", seconds=10
        )

        print("[CTFd Whale] Started successfully")
    except IOError:
        pass
