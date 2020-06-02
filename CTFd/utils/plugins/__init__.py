import json
import os
from collections import namedtuple
from pathlib import Path

from flask import current_app as app


def register_script(url):
    app.plugin_scripts.append(url)


def register_stylesheet(url):
    app.plugin_stylesheets.append(url)


def register_admin_script(url):
    app.admin_plugin_scripts.append(url)


def register_admin_stylesheet(url):
    app.admin_plugin_stylesheets.append(url)


def get_registered_scripts():
    return app.plugin_scripts


def get_registered_stylesheets():
    return app.plugin_stylesheets


def get_registered_admin_scripts():
    return app.admin_plugin_scripts


def get_registered_admin_stylesheets():
    return app.admin_plugin_stylesheets


def override_template(template, html):
    app.jinja_loader.overriden_templates[template] = html


def get_configurable_plugins():
    Plugin = namedtuple("Plugin", ["name", "route"])

    plugins_path = Path(app.root_path, "plugins")
    plugin_directories = (
        plugin_dir for plugin_dir in plugins_path.iterdir() if plugin_dir.is_dir()
    )

    config_files = [
        file
        for dir in plugin_directories
        for file in dir.iterdir()
        if file.name == "config"
    ]

    plugins = []

    for file in config_files:
        if file.suffix == ".json":
            with file.open() as f:
                plugin_json_data = json.loads(f.read())
                p = Plugin(
                    name=plugin_json_data.get("name"),
                    route=plugin_json_data.get("route"),
                )
                plugins.append(p)
        elif file.suffix == ".html":
            p = Plugin(name=dir, route="/admin/plugins/{}".format(dir))
            plugins.append(p)

    return plugins
