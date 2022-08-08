import json
import os
from collections import namedtuple

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
    app.overridden_templates[template] = html


def get_configurable_plugins():
    Plugin = namedtuple("Plugin", ["name", "route"])

    plugins_path = os.path.join(app.root_path, "plugins")
    plugin_directories = os.listdir(plugins_path)

    plugins = []

    for dir in plugin_directories:
        if os.path.isfile(os.path.join(plugins_path, dir, "config.json")):
            path = os.path.join(plugins_path, dir, "config.json")
            with open(path) as f:
                plugin_json_data = json.loads(f.read())
                if type(plugin_json_data) is list:
                    for plugin_json in plugin_json_data:
                        p = Plugin(
                            name=plugin_json.get("name"),
                            route=plugin_json.get("route"),
                        )
                        plugins.append(p)
                else:
                    p = Plugin(
                        name=plugin_json_data.get("name"),
                        route=plugin_json_data.get("route"),
                    )
                    plugins.append(p)
        elif os.path.isfile(os.path.join(plugins_path, dir, "config.html")):
            p = Plugin(name=dir, route="/admin/plugins/{}".format(dir))
            plugins.append(p)

    return plugins
