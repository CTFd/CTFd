from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash, abort, send_from_directory
from flask_restx import Namespace, Resource, Api

from CTFd.utils.decorators import authed_only, during_ctf_time_only, admins_only
from CTFd.utils.user import get_current_user, get_current_team, is_admin
from CTFd.models import db, Solves, Challenges, Notifications
from CTFd.models import Files
from CTFd.plugins import bypass_csrf_protection
from .models import PhotoSubmission
from werkzeug.utils import secure_filename
from CTFd.utils.uploads import upload_file
from CTFd.utils.uploads import get_uploader
from werkzeug.utils import safe_join
from flask import send_file
from datetime import datetime
from sqlalchemy.sql import func
import os, secrets
import json

# Attempt to load a local .env file in development (optional). If python-dotenv
# is installed this will read `.env` or `.flaskenv` near the project root so
# developers can keep secrets out of source control. In production (Docker,
# systemd, kubernetes) prefer passing environment variables via the runtime.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Optional server-side ntfy integration: set `PHOTO_NTFY_URL` in the app config
# to a full ntfy publish endpoint (e.g. https://ntfy.example.com/yourtopic).
# This URL is never exposed to clients; messages are sent from the backend only.

# photo_bp = Blueprint("photo_evidence", __name__, template_folder="templates", static_folder="static", url_prefix="/photo_evidence")
photo_namespace = Namespace("photos", description="Endpoint to handle photo evidence submissions")

# Dedicated API blueprint for plugin endpoints. Registering this blueprint
# with the app makes the plugin API available immediately without relying
# on the global CTFd_API_v1 initialization order.
photo_bp = Blueprint("photo_challenges_api", __name__, template_folder="templates")
photo_api = Api(photo_bp, doc=False)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _maybe_send_ntfy(challenge_id=None, challenge_name=None, team_id=None, submission_id=None):
    """Send a push to an ntfy endpoint if `PHOTO_NTFY_URL` is set in app config.

    The URL is read from `current_app.config['PHOTO_NTFY_URL']` and is never
    exposed to clients. Optionally configure `PHOTO_NTFY_HEADERS` as a dict of
    extra headers (e.g. Authorization) to include with the request.
    """
    ntfy_url = current_app.config.get('PHOTO_NTFY_URL')
    if not ntfy_url:
        return

    # Resolve challenge name if not provided
    if not challenge_name and challenge_id is not None:
        try:
            chal = Challenges.query.filter_by(id=challenge_id).first()
            if chal:
                challenge_name = chal.name
        except Exception:
            challenge_name = str(challenge_id)

    title = f"Photo submission: {challenge_name or challenge_id or 'unknown'}"
    body = f"Team {team_id} submitted a photo for '{challenge_name or challenge_id}'. Submission ID: {submission_id}"

    headers = {}
    # Prefer config, fall back to environment variable
    extra = current_app.config.get('PHOTO_NTFY_HEADERS') or os.environ.get('PHOTO_NTFY_HEADERS')
    if isinstance(extra, dict):
        headers.update(extra)
    elif isinstance(extra, str) and extra:
        # Allow JSON string in env var: PHOTO_NTFY_HEADERS='{"Authorization":"Basic ..."}'
        try:
            parsed = json.loads(extra)
            if isinstance(parsed, dict):
                headers.update(parsed)
        except Exception:
            # ignore parse errors
            pass
    # ntfy supports a "Title" header for notifications
    headers.setdefault('Title', title)

    # Try requests first, fall back to urllib
    try:
        # Try requests if available
        try:
            import requests
            requests.post(ntfy_url, data=body.encode('utf-8'), headers=headers, timeout=5)
            return
        except Exception:
            pass

        # Fallback to urllib
        from urllib.request import Request, urlopen
        req = Request(ntfy_url, data=body.encode('utf-8'), headers=headers)
        urlopen(req, timeout=5)
    except Exception as e:
        current_app.logger.exception("photo_challenges: ntfy send failed: %s", e)

@photo_bp.route("/upload/<int:challenge_id>", methods=["GET","POST"])
@authed_only
@during_ctf_time_only
@bypass_csrf_protection
def upload(challenge_id):
    if request.method == "POST":
        if "photo" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
        file = request.files["photo"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Invalid file type", "danger")
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filename = f"{secrets.token_hex(8)}_{filename}"
        # Use CTFd uploader (honors UPLOAD_FOLDER or S3) to store files in a writable location
        location = f"photo_evidence/{filename}"
        file_row = upload_file(file=file, challenge_id=challenge_id, type="challenge", location=location)
        path = file_row.location

        user = get_current_user()
        team = get_current_team()
        team_id = team.id if team else (user.id if user else None)
        submission = PhotoSubmission(team_id=team_id, challenge_id=challenge_id, filename=filename, filepath=path)
        db.session.add(submission)
        db.session.commit()

        # Mark the challenge as paused (pending review) so teams see it's awaiting verification
        try:
            chal = Challenges.query.filter_by(id=challenge_id).first()
            if chal:
                chal.state = "paused"
                db.session.commit()
        except Exception:
            db.session.rollback()

        # Notify the team that their submission is pending review
        challenge_name = None
        try:
            chal = Challenges.query.filter_by(id=challenge_id).first()
            challenge_name = chal.name if chal else str(challenge_id)
            note = Notifications(title="Photo submission pending", content=f"Your photo submission for challenge '{challenge_name}' is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Send optional server-side ntfy push (kept secret on server)
        try:
            _maybe_send_ntfy(challenge_name=challenge_name, team_id=team_id, submission_id=submission.id)
        except Exception:
            current_app.logger.exception("photo_challenges: ntfy push failed")
        
        flash("Photo submitted for review", "success")
        return redirect(url_for("challenges.view", challenge_id=challenge_id))

    challenge = Challenges.query.filter_by(id=challenge_id).first()
    return render_template("upload.html", challenge=challenge)

@photo_namespace.route("/solve/<subflag_id>")
class Solve(Resource):
    """Accepts a file upload for a photo challenge and creates a pending PhotoSubmission."""
    @authed_only
    def post(self, subflag_id):
        # support either 'file' or 'photo' field names
        file = None
        if "file" in request.files:
            file = request.files["file"]
        elif "photo" in request.files:
            file = request.files["photo"]

        if file is None or file.filename == "":
            return {"success": False, "message": "No file uploaded"}, 400

        if not allowed_file(file.filename):
            return {"success": False, "message": "Invalid file type"}, 400

        filename = secure_filename(file.filename)
        filename = f"{secrets.token_hex(8)}_{filename}"
        location = f"photo_evidence/{filename}"
        file_row = upload_file(file=file, challenge_id=subflag_id, type="challenge", location=location)
        path = file_row.location

        user = get_current_user()
        team = get_current_team()
        team_id = team.id if team else (user.id if user else None)

        submission = PhotoSubmission(team_id=team_id, challenge_id=subflag_id, filename=filename, filepath=path)
        db.session.add(submission)
        db.session.commit()

        # Mark the challenge as paused (pending review)
        try:
            chal = Challenges.query.filter_by(id=subflag_id).first()
            if chal:
                chal.state = "paused"
                db.session.commit()
        except Exception:
            db.session.rollback()

        # Notify the team
        challenge_name = None
        try:
            chal = Challenges.query.filter_by(id=subflag_id).first()
            challenge_name = chal.name if chal else str(subflag_id)
            note = Notifications(title="Photo submission pending", content=f"Your photo submission for challenge '{challenge_name}' is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Send optional server-side ntfy push
        try:
            _maybe_send_ntfy(challenge_name=challenge_name, team_id=team_id, submission_id=submission.id)
        except Exception:
            current_app.logger.exception("photo_challenges: ntfy push failed")

        return {"success": True, "message": "Photo submitted for review", "submission_id": submission.id}

@photo_namespace.route("/upload", methods=["POST"])
class UploadPhoto(Resource):
    """API endpoint to accept a photo upload for a challenge (RESTX Resource)."""
    method_decorators = [authed_only, bypass_csrf_protection]

    def post(self):
        if "file" not in request.files:
            return {"success": False, "message": "No file"}, 400

        file = request.files["file"]
        challenge_id = request.form.get("challenge_id")

        if not file or not challenge_id:
            return {"success": False, "message": "Invalid submission"}, 400

        if not allowed_file(file.filename):
            return {"success": False, "message": "Invalid file type"}, 400

        filename = secure_filename(file.filename)
        filename = f"{secrets.token_hex(8)}_{filename}"
        location = f"photo_evidence/{filename}"
        file_row = upload_file(file=file, challenge_id=int(challenge_id), type="challenge", location=location)
        path = file_row.location

        user = get_current_user()
        team = get_current_team()
        team_id = team.id if team else (user.id if user else None)

        submission = PhotoSubmission(team_id=team_id, challenge_id=int(challenge_id), filename=filename, filepath=path)
        db.session.add(submission)
        db.session.commit()

        # Mark the challenge as paused (pending review)
        try:
            chal = Challenges.query.filter_by(id=int(challenge_id)).first()
            if chal:
                chal.state = "paused"
                db.session.commit()
        except Exception:
            db.session.rollback()

        # Notify the team
        challenge_name = None
        try:
            chal = Challenges.query.filter_by(id=int(challenge_id)).first()
            challenge_name = chal.name if chal else str(challenge_id)
            note = Notifications(title="Photo submission pending", content=f"Your photo submission for challenge '{challenge_name}' is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Send optional server-side ntfy push
        try:
            _maybe_send_ntfy(challenge_name=challenge_name, team_id=team_id, submission_id=submission.id)
        except Exception:
            current_app.logger.exception("photo_challenges: ntfy push failed")

        return {"success": True, "message": "Photo submitted for review", "submission_id": submission.id}


@photo_namespace.route("/status/<int:challenge_id>")
class SubmissionStatus(Resource):
    """Return whether the current user/team has a pending submission for the challenge."""
    method_decorators = [authed_only]

    def get(self, challenge_id):
        user = get_current_user()
        team = get_current_team()
        team_id = team.id if team else (user.id if user else None)

        status = None
        if team_id is not None:
            sub = (
                PhotoSubmission.query.filter_by(team_id=team_id, challenge_id=challenge_id)
                .order_by(PhotoSubmission.submitted_at.desc())
                .first()
            )
            if sub:
                status = sub.status

        return {"status": status}


# Admin review UI and actions
@photo_namespace.route("/admin/review")
class AdminReview(Resource):
    method_decorators = [admins_only]

    def get(self):
        # list pending submissions
        # Only include submissions whose file record still exists in the Files/ChallengeFiles table
        submissions = (
            PhotoSubmission.query.order_by(PhotoSubmission.submitted_at.desc()).all()
        )
        valid_submissions = []
        for s in submissions:
            if s.filepath and Files.query.filter_by(location=s.filepath).first():
                valid_submissions.append(s)

        # Render the admin review HTML. Some admin UI code fetches this
        # endpoint via XHR and expects JSON. Detect Accept header and
        # return JSON-wrapped HTML when appropriate to avoid the UI
        # attempting to parse HTML as JSON.
        rendered = render_template('admin_review.html', submissions=valid_submissions)
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept:
            return {'html': rendered}

        return rendered


@photo_namespace.route('/admin/review/<int:submission_id>/approve', methods=['POST'])
class AdminApprove(Resource):
    method_decorators = [admins_only]

    def post(self, submission_id):
        sub = PhotoSubmission.query.filter_by(id=submission_id).first_or_404()
        sub.status = 'approved'
        sub.reviewed_at = datetime.utcnow()
        sub.review_notes = request.form.get('notes', '')
        db.session.add(sub)

        # award solve if not already solved for this team/user
        try:
            chal = Challenges.query.filter_by(id=sub.challenge_id).first()
            if chal:
                chal.state = 'visible'
            # Create a Solves record if not exists
            existing_solve = Solves.query.filter_by(challenge_id=sub.challenge_id, team_id=sub.team_id).first()
            if not existing_solve:
                solve = Solves(challenge_id=sub.challenge_id, user_id=None, team_id=sub.team_id, ip=None, provided=sub.filename)
                db.session.add(solve)
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Notify team with details and mark other pending submissions cleared
        try:
            chal = Challenges.query.filter_by(id=sub.challenge_id).first()
            challenge_name = chal.name if chal else str(sub.challenge_id)
            content = f"Your photo submission for challenge '{challenge_name}' was approved."
            if sub.review_notes:
                content += f"\nReview notes: {sub.review_notes}"

            note = Notifications(title='Photo submission approved', content=content, team_id=sub.team_id)
            db.session.add(note)
            # Mark any other pending submissions for this team/challenge as rejected/cleared
            PhotoSubmission.query.filter_by(team_id=sub.team_id, challenge_id=sub.challenge_id, status='pending').update({"status": "rejected"})
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Return JSON for XHR/JSON clients, otherwise redirect to the
        # admin review page so browser form submits still work.
        rendered = render_template('admin_review.html', submissions=PhotoSubmission.query.order_by(PhotoSubmission.submitted_at.desc()).all())
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": True, "submission_id": sub.id, "status": "approved", "html": rendered}
        return redirect('/api/v1/photo_challenges/admin/review')


@photo_namespace.route('/admin/review/<int:submission_id>/reject', methods=['POST'])
class AdminReject(Resource):
    method_decorators = [admins_only]

    def post(self, submission_id):
        sub = PhotoSubmission.query.filter_by(id=submission_id).first_or_404()
        sub.status = 'rejected'
        sub.reviewed_at = datetime.utcnow()
        sub.review_notes = request.form.get('notes', '')
        db.session.add(sub)
        try:
            # set challenge visible so team can resubmit
            chal = Challenges.query.filter_by(id=sub.challenge_id).first()
            if chal:
                chal.state = 'visible'
            db.session.commit()
        except Exception:
            db.session.rollback()

        # Notify team and ensure any pending flags are cleared so challenge is submittable
        try:
            chal = Challenges.query.filter_by(id=sub.challenge_id).first()
            challenge_name = chal.name if chal else str(sub.challenge_id)
            content = f"Your photo submission for challenge '{challenge_name}' was rejected."
            if sub.review_notes:
                content += f"\nReview notes: {sub.review_notes}"

            note = Notifications(title='Photo submission rejected', content=content, team_id=sub.team_id)
            db.session.add(note)
            # Clear any other pending submissions for this team/challenge
            PhotoSubmission.query.filter_by(team_id=sub.team_id, challenge_id=sub.challenge_id, status='pending').update({"status": "rejected"})
            # Ensure challenge is visible/submittable again
            if chal:
                chal.state = 'visible'
            db.session.commit()
        except Exception:
            db.session.rollback()

        rendered = render_template('admin_review.html', submissions=PhotoSubmission.query.order_by(PhotoSubmission.submitted_at.desc()).all())
        accept = request.headers.get('Accept', '')
        if 'application/json' in accept or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"success": True, "submission_id": sub.id, "status": "rejected", "html": rendered}
        return redirect('/api/v1/photo_challenges/admin/review')


@photo_namespace.route('/admin/file/<path:filename>')
class AdminFile(Resource):
    method_decorators = [admins_only]

    def get(self, filename):
        # Ensure a Files record exists for this location
        f = Files.query.filter_by(location=filename).first()
        if not f:
            current_app.logger.info("photo_challenges: admin file requested but DB record missing: %s", filename)
            abort(404)

        uploader = get_uploader()
        # Prefer serving local filesystem files inline; log diagnostic info so container logs show what's happening
        try:
            base = getattr(uploader, "base_path", None)
            current_app.logger.info("photo_challenges: serving admin file %s using uploader=%s base=%s", filename, type(uploader).__name__, base)
            if base:
                # compute path and verify existence explicitly
                file_path = os.path.join(base, filename)
                current_app.logger.info("photo_challenges: computed file_path=%s exists=%s", file_path, os.path.exists(file_path))
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    return send_file(file_path, as_attachment=False)

            # Fall back to uploader.download (e.g., S3 redirect) if local file not found
            current_app.logger.info("photo_challenges: falling back to uploader.download for %s", filename)
            return uploader.download(filename)
        except Exception as e:
            current_app.logger.exception("photo_challenges: error serving admin file %s: %s", filename, e)
            abort(404)


# Admin UI landing page mapped to `/admin/photo_evidence` (plugin menu target)
@admins_only
def admin_page():
    """Render the admin review template so the admin menu link works."""
    submissions = PhotoSubmission.query.order_by(PhotoSubmission.submitted_at.desc()).all()
    valid_submissions = []
    for s in submissions:
        if s.filepath and Files.query.filter_by(location=s.filepath).first():
            valid_submissions.append(s)

    return render_template('admin_review.html', submissions=valid_submissions)


# --- Fallback view functions (used by plugin load to register direct Flask rules) ---
def upload_photo_fallback():
    """Fallback view that delegates to the API upload handler.

    This exists so `__init__.py` can register a direct Flask URL rule
    in environments where the RESTX namespace isn't attached yet.
    """
    # Mirror the logic from the UploadPhoto Resource.post
    if "file" not in request.files:
        return {"success": False, "message": "No file"}, 400

    file = request.files["file"]
    challenge_id = request.form.get("challenge_id")

    if not file or not challenge_id:
        return {"success": False, "message": "Invalid submission"}, 400

    if not allowed_file(file.filename):
        return {"success": False, "message": "Invalid file type"}, 400

    filename = secure_filename(file.filename)
    filename = f"{secrets.token_hex(8)}_{filename}"
    location = f"photo_evidence/{filename}"
    file_row = upload_file(file=file, challenge_id=int(challenge_id), type="challenge", location=location)
    path = file_row.location

    user = get_current_user()
    team = get_current_team()
    team_id = team.id if team else (user.id if user else None)

    submission = PhotoSubmission(team_id=team_id, challenge_id=int(challenge_id), filename=filename, filepath=path)
    db.session.add(submission)
    db.session.commit()

    # Mark the challenge as paused (pending review)
    try:
        chal = Challenges.query.filter_by(id=int(challenge_id)).first()
        if chal:
            chal.state = "paused"
            db.session.commit()
    except Exception:
        db.session.rollback()

    # Notify the team
    try:
        note = Notifications(title="Photo submission pending", content=f"Your photo for challenge {challenge_id} is pending review.", team_id=team_id)
        db.session.add(note)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return {"success": True, "message": "Photo submitted for review", "submission_id": submission.id}


def submission_status_fallback(challenge_id):
    """Fallback view that delegates to the submission status handler."""
    user = get_current_user()
    team = get_current_team()
    team_id = team.id if team else (user.id if user else None)

    status = None
    if team_id is not None:
        sub = (
            PhotoSubmission.query.filter_by(team_id=team_id, challenge_id=challenge_id)
            .order_by(PhotoSubmission.submitted_at.desc())
            .first()
        )
        if sub:
            status = sub.status

    return {"status": status}
