from collections import namedtuple
from flask import current_app as app
import os
import json


SCRIPTS = []
STYLESHEETS = []


def register_script(url):
    SCRIPTS.append(url)


def register_stylesheet(url):
    STYLESHEETS.append(url)


def get_registered_scripts():
    return SCRIPTS


def get_registered_stylesheets():
    return STYLESHEETS


def override_template(template, html):
    app.jinja_loader.overriden_templates[template] = html


def get_configurable_plugins():
    Plugin = namedtuple('Plugin', ['name', 'route'])

    plugins_path = os.path.join(app.root_path, 'plugins')
    plugin_directories = os.listdir(plugins_path)

    plugins = []

    for dir in plugin_directories:
        if os.path.isfile(os.path.join(plugins_path, dir, 'config.json')):
            path = os.path.join(plugins_path, dir, 'config.json')
            with open(path) as f:
                plugin_json_data = json.loads(f.read())
                p = Plugin(
                    name=plugin_json_data.get('name'),
                    route=plugin_json_data.get('route')
                )
                plugins.append(p)
        elif os.path.isfile(os.path.join(plugins_path, dir, 'config.html')):
            p = Plugin(
                name=dir,
                route='/admin/plugins/{}'.format(dir)
            )
            plugins.append(p)

    return plugins
