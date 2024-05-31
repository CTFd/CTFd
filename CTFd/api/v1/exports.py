from datetime import datetime as DateTime

from flask import request, send_file
from flask_restx import Namespace, Resource

from CTFd.utils.config import ctf_name
from CTFd.utils.csv import dump_csv
from CTFd.utils.decorators import admins_only, ratelimit
from CTFd.utils.exports import export_ctf as export_ctf_util

exports_namespace = Namespace("exports", description="Endpoint to retrieve Exports")


@exports_namespace.route("/raw")
class ExportList(Resource):
    @admins_only
    @ratelimit(method="POST", limit=10, interval=60)
    def post(self):
        req = request.get_json()
        export_type = req.get("type", "_")
        export_args = req.get("args", {})

        day = DateTime.now().strftime("%Y-%m-%d_%T")
        if export_type == "csv":
            table = export_args.get("table")
            if not table:
                return {
                    "success": False,
                    "errors": {"args": "Missing table to export"},
                }, 400
            output = dump_csv(name=table)
            return send_file(
                output,
                as_attachment=True,
                max_age=-1,
                download_name=f"{ctf_name()}-{table}-{day}.csv",
            )
        else:
            backup = export_ctf_util()
            full_name = f"{ctf_name()}.{day}.zip"
            return send_file(
                backup,
                cache_timeout=-1,
                as_attachment=True,
                attachment_filename=full_name,
            )
