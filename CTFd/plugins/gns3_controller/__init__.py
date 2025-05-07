import os
from flask import Blueprint, jsonify, request
from CTFd.plugins import register_plugin_assets_directory
from CTFd.utils.decorators import authed_only
import requests

def load(app):
    gns3_bp = Blueprint(
        'gns3_controller', __name__,
        template_folder='templates',
        static_folder='assets',
        url_prefix='/plugins/gns3_controller'
    )

    # Route for starting a GNS3 project
    @gns3_bp.route('/start/<project_id>', methods=['GET'])
    # @authed_only  # Optional: Uncomment to require user authentication
    def start_gns3_project(project_id):
        try:
            gns3_url = f"http://192.168.1.124/v2/projects/{project_id}"
            response = requests.get(gns3_url)
            print(f"[DEBUG] Status check response code: {response.status_code}")

            if response.status_code == 200:
                project_status = response.json().get('status')
                if project_status == 'opened':
                    return jsonify({
                        "status": "already_opened",
                        "message": "The project is already opened.",
                        "code": response.status_code
                    })

                gns3_open_url = f"http://192.168.1.124/v2/projects/{project_id}/open"
                open_response = requests.post(gns3_open_url)
                print(f"[DEBUG] Open project response code: {open_response.status_code}")

                if open_response.status_code in [200, 201, 204]:
                    return jsonify({
                        "status": "started",
                        "code": open_response.status_code
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "response": open_response.text,
                        "code": open_response.status_code
                    }), 500
            else:
                return jsonify({
                    "status": "error",
                    "response": response.text,
                    "code": response.status_code
                }), 500
        except Exception as e:
            return jsonify({
                "status": "exception",
                "error": str(e),
                "code": "exception"
            }), 500

    register_plugin_assets_directory(app, base_path="/plugins/gns3_controller/assets/")
    app.register_blueprint(gns3_bp)
