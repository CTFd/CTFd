from flask import Blueprint, render_template, request

from CTFd.models import Users, Teams, Files
from CTFd.utils import get_config, set_config, config
from CTFd.utils.decorators import authed_only, admins_only, ratelimit
from CTFd.utils.user import get_current_user
from CTFd.utils.uploads import upload_file

writeups = Blueprint("writeups", __name__)

def writeups_upload_enabled(toggle=None):
    if(toggle != None):
        set_config("writeups_upload_enabled", toggle)
        return toggle
    else:
        return get_config("writeups_upload_enabled", False)

def check_allow_extension(filename=""):
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = get_config(
        "writeups_allow_extension", "pdf, md"
    ).replace(" ", "").split(",")
    if ext in allowed:
        return ext
    return False

@writeups.route("/writeups")
@authed_only
def index():
    enabled = writeups_upload_enabled()
    return render_template("writeups.html", enabled=enabled)

@writeups.route("/writeups/upload", methods=["GET", "POST"])
@authed_only
def upload():
    if(not writeups_upload_enabled()):
        return {"success": False, "errors": "Not enabled"}, 400
    user = get_current_user()
    account = user.account
    prefix = "Team" if config.is_teams_mode() else "User"
    if config.is_teams_mode() and account is None:
        return {"success": False, "errors": "You dont belongs to any team"}, 400
    file = request.files.get("file")
    if not file or file.filename == "":
        return {"success": False, "errors": "No file provided"}, 400
    ext = check_allow_extension(file.filename)
    if ext == False:
        return {"success": False, "errors": "Bad file extension"}, 400
    upload_file(file=file, location=f"writeups/{prefix}-a{account.id}-u{user.id}.{ext}")
    return {"success": True, "message": "Done"}, 201


@writeups.route("/writeups/list")
@admins_only
def listing():
    files = Files.query.filter(Files.location.like("writeups/%")).all()
    result = []
    for file in files:
        filename = file.location.rsplit("/", 1)[1]
        result.append(filename)

    return {"success": True, "data": result}, 200


@writeups.route("/writeups/settings")
@admins_only
def setting():
    enabled = request.args.get("enabled", None)
    extensions = request.args.get("extensions", None)
    enabled_result = writeups_upload_enabled(enabled)
    if type(extensions) == str:
        set_config("writeups_allow_extension", extensions)
    extensions_result = get_config("writeups_allow_extension", "pdf, md")

    return {"success": True, "data": {
        "enabled": enabled_result,
        "extensions": extensions_result.replace(" ", "").split(",")
    }}, 200

