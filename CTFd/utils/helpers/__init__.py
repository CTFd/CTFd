from flask import (
    request,
    flash,
    get_flashed_messages,
    url_for as flask_url_for,
    current_app
)
import os


def info_for(endpoint, message):
    flash(message=message, category=endpoint + ".infos")


def error_for(endpoint, message):
    flash(message=message, category=endpoint + ".errors")


def get_infos():
    return get_flashed_messages(category_filter=request.endpoint + ".infos")


def get_errors():
    return get_flashed_messages(category_filter=request.endpoint + ".errors")


def url_for(endpoint, **values):
    if endpoint == 'views.themes':
        path = values.get('path', '')
        static_asset = path.endswith('.js') or path.endswith('.css')
        direct_access = '.dev' in path or '.min' in path
        if static_asset and not direct_access:
            env = values.get('env', current_app.env)
            mode = '.dev' if env == 'development' else '.min'
            base, ext = os.path.splitext(path)
            values['path'] = base + mode + ext
    return flask_url_for(endpoint, **values)
