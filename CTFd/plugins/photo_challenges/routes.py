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
        try:
            note = Notifications(title="Photo submission pending", content=f"Your photo for challenge {challenge_id} is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()
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
        try:
            note = Notifications(title="Photo submission pending", content=f"Your photo for challenge {subflag_id} is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

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
        try:
            note = Notifications(title="Photo submission pending", content=f"Your photo for challenge {challenge_id} is pending review.", team_id=team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return {"success": True, "message": "Photo submitted for review", "submission_id": submission.id}


@photo_namespace.route("/status/<int:challenge_id>")
class SubmissionStatus(Resource):
    """Return whether the current user/team has a pending submission for the challenge."""
    method_decorators = [authed_only]

    def get(self, challenge_id):
        user = get_current_user()
        team = get_current_team()
        team_id = team.id if team else (user.id if user else None)

        pending = False
        if team_id is not None:
            pending = PhotoSubmission.query.filter_by(team_id=team_id, challenge_id=challenge_id, status='pending').first() is not None

        return {"pending": pending}


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

        return render_template('admin_review.html', submissions=valid_submissions)


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

        # Notify team
        try:
            note = Notifications(title='Photo submission approved', content=f'Your photo submission for challenge {sub.challenge_id} was approved.', team_id=sub.team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

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

        try:
            note = Notifications(title='Photo submission rejected', content=f'Your photo submission for challenge {sub.challenge_id} was rejected.', team_id=sub.team_id)
            db.session.add(note)
            db.session.commit()
        except Exception:
            db.session.rollback()

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
