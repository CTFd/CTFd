import datetime
import functools

from flask import Blueprint, abort, jsonify, request, session

from CTFd.constants.git import Git
from CTFd.models import UserTokens, db
from CTFd.utils import get_config, set_config
from CTFd.utils.config import is_setup
from CTFd.utils.git import (
    CTFCLI_CONFIG_PATH,
    GitError,
    ctfcli_scaffold,
    get_provider,
)
from CTFd.utils.security.auth import generate_user_token
from CTFd.utils.user import get_current_user, is_admin

git = Blueprint("git", __name__, url_prefix="/setup/git")


def provision_ctfcli_integration(provider, provider_token, repo, user):
    old_token_id = get_config("git_token_id")
    token = generate_user_token(
        user,
        expiration=datetime.datetime.utcnow() + datetime.timedelta(days=365),
        description="ctfcli challenge sync token",
    )
    try:
        provider.provision_credentials(
            provider_token,
            repo,
            ctfd_url=request.host_url.rstrip("/"),
            ctfd_token=token.value,
        )
        if repo.get("needs_ci"):
            provider.create_files(
                provider_token,
                repo,
                files={provider.ci_path: provider.ci_file},
                message="Add challenge sync pipeline",
            )
            repo["needs_ci"] = False
    except Exception:
        db.session.delete(token)
        db.session.commit()
        raise

    if old_token_id:
        old_token = UserTokens.query.filter_by(id=old_token_id).first()
        if old_token:
            db.session.delete(old_token)
            db.session.commit()

    set_config("git_provider", provider.id)
    set_config("git_repository", repo["name"])
    set_config("git_token_id", token.id)


def git_managers_only(f):
    """
    Decorator gating the git connector endpoints: during setup they are open
    (no accounts exist yet); once the instance is set up they are only
    available to admins managing the integration.
    """

    @functools.wraps(f)
    def git_managers_only_wrapper(*args, **kwargs):
        if is_setup() and not is_admin():
            abort(403)
        return f(*args, **kwargs)

    return git_managers_only_wrapper


def git_session(provider_id):
    integration = session.get("setup_git")
    if not integration or integration.get("provider") != provider_id:
        raise GitError("Not connected to this provider", status_code=401)
    return integration


@git.errorhandler(GitError)
def handle_git_error(error):
    return jsonify({"success": False, "errors": [error.message]}), error.status_code


@git.route("", methods=["GET", "DELETE"])
@git_managers_only
def repository():
    if request.method == "DELETE":
        session.pop("setup_git", None)
        session.pop("setup_git_device", None)
        if is_setup():
            # Disconnecting a provisioned integration also revokes the sync
            # token so the repository CI loses access to the instance.
            token_id = get_config("git_token_id")
            if token_id:
                token = UserTokens.query.filter_by(id=token_id).first()
                if token:
                    db.session.delete(token)
                    db.session.commit()
            set_config("git_provider", None)
            set_config("git_repository", None)
            set_config("git_token_id", None)
        return jsonify({"success": True})

    integration = session.get("setup_git") or {}
    repo = integration.get("repo") or None
    return jsonify(
        {
            "success": True,
            "data": {
                "providers": Git.providers,
                "provider": integration.get("provider"),
                "user": integration.get("user"),
                "repository": repo,
                "configured": {
                    "provider": Git.provider,
                    "repository": Git.repository,
                },
            },
        }
    )


@git.route("/<provider_id>/device", methods=["POST"])
@git_managers_only
def device(provider_id):
    provider = get_provider(provider_id)
    data = provider.device_authorization()
    session["setup_git_device"] = {
        "provider": provider_id,
        "device_code": data.pop("device_code"),
    }
    return jsonify({"success": True, "data": data})


@git.route("/<provider_id>/device/token", methods=["POST"])
@git_managers_only
def device_token(provider_id):
    provider = get_provider(provider_id)
    device = session.get("setup_git_device")
    if not device or device.get("provider") != provider_id:
        raise GitError("No device login in progress")
    result = provider.device_token(device["device_code"])
    if result["status"] == "ok":
        user = provider.get_user(result["token"])
        session.pop("setup_git_device", None)
        session["setup_git"] = {
            "provider": provider_id,
            "token": result["token"],
            "user": user,
        }
        return jsonify({"success": True, "data": {"status": "ok", "user": user}})
    elif result["status"] == "pending":
        return jsonify({"success": True, "data": {"status": "pending"}})
    raise GitError(result.get("message", "Device login failed"))


@git.route("/<provider_id>/token", methods=["POST"])
@git_managers_only
def token(provider_id):
    provider = get_provider(provider_id)
    token = ((request.get_json(silent=True) or {}).get("token") or "").strip()
    if not token:
        raise GitError("Please provide an access token")
    user = provider.get_user(token)
    session["setup_git"] = {
        "provider": provider_id,
        "token": token,
        "user": user,
    }
    return jsonify({"success": True, "data": {"user": user}})


@git.route("/<provider_id>/repositories", methods=["GET", "POST"])
@git_managers_only
def repositories(provider_id):
    provider = get_provider(provider_id)
    integration = git_session(provider_id)
    token = integration["token"]

    if request.method == "GET":
        return jsonify({"success": True, "data": provider.list_repositories(token)})

    req = request.get_json(silent=True) or {}
    action = req.get("action")
    ctfd_url = request.host_url.rstrip("/")

    if action == "select":
        requested = req.get("repository") or {}
        if not requested.get("id"):
            raise GitError("Please select a repository")
        repo = {
            "id": requested["id"],
            "name": requested.get("name") or str(requested["id"]),
            "default_branch": requested.get("default_branch") or "main",
        }
        if not provider.has_file(token, repo, CTFCLI_CONFIG_PATH):
            raise GitError(
                "The selected repository is not a valid ctfcli project "
                "(it does not contain a .ctf/config file)"
            )
        # The CI file is committed at setup completion, after the CI
        # credentials exist; committing it now would trigger a pipeline run
        # that fails because the secrets are not set yet.
        repo["needs_ci"] = not provider.has_file(token, repo, provider.ci_path)
    elif action == "create":
        name = (req.get("name") or "").strip()
        if not name:
            raise GitError("Please provide a repository name")
        repo = provider.create_repository(
            token, name, private=bool(req.get("private", True))
        )
        # Scaffolds .ctf/config and README only; the CI file follows at setup
        # completion once the credentials it needs are in place.
        provider.create_files(
            token,
            repo,
            files=ctfcli_scaffold(repo, ctfd_url),
            message="Initialize ctfcli project",
        )
        repo["needs_ci"] = True
    else:
        raise GitError("Unknown action")

    provisioned = False
    if is_setup():
        # Admins manage the integration on a live instance, so there is no
        # later finalization step: provision the credentials and CI file now.
        provision_ctfcli_integration(provider, token, repo, user=get_current_user())
        provisioned = True

    integration["repo"] = repo
    session["setup_git"] = integration
    return jsonify(
        {
            "success": True,
            "data": {
                "repository": repo,
                "ci_pending": repo["needs_ci"],
                "provisioned": provisioned,
            },
        }
    )
