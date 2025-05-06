import os
from flask import request
from CTFd.plugins import register_plugin_assets_directory


def load(app):
    # Register the assets directory for the plugin
    register_plugin_assets_directory(app, base_path="/plugins/test_button_plugin/assets")

    @app.after_request
    def inject_clickme_script(response):
        # Only inject on the /challenges route (not static API calls)
        if request.path == "/challenges":
            script_tag = '<script src="/plugins/test_button_plugin/assets/clickme.js"></script>'
            if b"</body>" in response.data:
                response.data = response.data.replace(b"</body>", script_tag.encode() + b"</body>")
        return response
