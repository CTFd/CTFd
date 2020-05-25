try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
from flask import current_app, flash, get_flashed_messages, request


def info_for(endpoint, message):
    flash(message=message, category=endpoint + ".infos")


def error_for(endpoint, message):
    flash(message=message, category=endpoint + ".errors")


def get_infos():
    return get_flashed_messages(category_filter=request.endpoint + ".infos")


def get_errors():
    return get_flashed_messages(category_filter=request.endpoint + ".errors")


@current_app.url_defaults
def env_asset_url_default(endpoint, values):
    """Create asset URLs dependent on the current env"""
    if endpoint == "views.themes":
        path = values.get("path", "")
        static_asset = path.endswith(".js") or path.endswith(".css")
        direct_access = ".dev" in path or ".min" in path
        if static_asset and not direct_access:
            env = values.get("env", current_app.env)
            mode = ".dev" if env == "development" else ".min"
            path = Path(path)
            values["path"] = str(path.parent.joinpath(path.stem, mode, path.suffix))


@current_app.url_defaults
def asset_cache_url_default(endpoint, values):
    """Used to cache bust per server restarts"""
    if endpoint == "views.themes":
        values["d"] = current_app.run_id
