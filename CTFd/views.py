import os  # noqa: I001

from flask import Blueprint, abort
from flask import current_app as app
from flask import (
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from jinja2.exceptions import TemplateNotFound
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import safe_join

from CTFd.cache import cache
from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    ConfigTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.constants.themes import DEFAULT_THEME
from CTFd.models import (
    Admins,
    Files,
    Notifications,
    Pages,
    Teams,
    Users,
    UserTokens,
    db,
)
from CTFd.utils import config, get_config, set_config
from CTFd.utils import user as current_user
from CTFd.utils import validators
from CTFd.utils.config import is_setup, is_teams_mode
from CTFd.utils.config.pages import build_markdown, get_page
from CTFd.utils.config.visibility import challenges_visible
from CTFd.utils.dates import ctf_ended, ctftime, view_after_ctf
from CTFd.utils.decorators import authed_only
from CTFd.utils.email import (
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)
from CTFd.utils.health import check_config, check_database
from CTFd.utils.helpers import get_errors, get_infos, markup
from CTFd.utils.modes import USERS_MODE
from CTFd.utils.security.auth import login_user
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    serialize,
    unserialize,
)
from CTFd.utils.uploads import get_uploader, upload_file
from CTFd.utils.user import authed, get_current_team, get_current_user, get_ip, is_admin

views = Blueprint("views", __name__)


@views.route("/setup", methods=["GET", "POST"])
def setup():
    errors = get_errors()
    if not config.is_setup():
        if not session.get("nonce"):
            session["nonce"] = generate_nonce()
        if request.method == "POST":
            # General
            ctf_name = request.form.get("ctf_name")
            ctf_description = request.form.get("ctf_description")
            user_mode = request.form.get("user_mode", USERS_MODE)
            set_config("ctf_name", ctf_name)
            set_config("ctf_description", ctf_description)
            set_config("user_mode", user_mode)

            # Settings
            challenge_visibility = ChallengeVisibilityTypes(
                request.form.get(
                    "challenge_visibility", default=ChallengeVisibilityTypes.PRIVATE
                )
            )
            account_visibility = AccountVisibilityTypes(
                request.form.get(
                    "account_visibility", default=AccountVisibilityTypes.PUBLIC
                )
            )
            score_visibility = ScoreVisibilityTypes(
                request.form.get(
                    "score_visibility", default=ScoreVisibilityTypes.PUBLIC
                )
            )
            registration_visibility = RegistrationVisibilityTypes(
                request.form.get(
                    "registration_visibility",
                    default=RegistrationVisibilityTypes.PUBLIC,
                )
            )
            verify_emails = request.form.get("verify_emails")
            team_size = request.form.get("team_size")

            # Style
            ctf_logo = request.files.get("ctf_logo")
            if ctf_logo:
                f = upload_file(file=ctf_logo)
                set_config("ctf_logo", f.location)

            ctf_small_icon = request.files.get("ctf_small_icon")
            if ctf_small_icon:
                f = upload_file(file=ctf_small_icon)
                set_config("ctf_small_icon", f.location)

            theme = request.form.get("ctf_theme", DEFAULT_THEME)
            set_config("ctf_theme", theme)
            theme_color = request.form.get("theme_color")
            theme_header = get_config("theme_header")
            if theme_color and bool(theme_header) is False:
                # Uses {{ and }} to insert curly braces while using the format method
                css = (
                    '<style id="theme-color">\n'
                    ":root {{--theme-color: {theme_color};}}\n"
                    ".navbar{{background-color: var(--theme-color) !important;}}\n"
                    ".jumbotron{{background-color: var(--theme-color) !important;}}\n"
                    "</style>\n"
                ).format(theme_color=theme_color)
                set_config("theme_header", css)

            # DateTime
            start = request.form.get("start")
            end = request.form.get("end")
            set_config("start", start)
            set_config("end", end)
            set_config("freeze", None)

            # Administration
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

            name_len = len(name) == 0
            names = (
                Users.query.add_columns(Users.name, Users.id)
                .filter_by(name=name)
                .first()
            )
            emails = (
                Users.query.add_columns(Users.email, Users.id)
                .filter_by(email=email)
                .first()
            )
            pass_short = len(password) == 0
            pass_long = len(password) > 128
            valid_email = validators.validate_email(request.form["email"])
            team_name_email_check = validators.validate_email(name)

            if not valid_email:
                errors.append("Please enter a valid email address")
            if names:
                errors.append("That user name is already taken")
            if team_name_email_check is True:
                errors.append("Your user name cannot be an email address")
            if emails:
                errors.append("That email has already been used")
            if pass_short:
                errors.append("Pick a longer password")
            if pass_long:
                errors.append("Pick a shorter password")
            if name_len:
                errors.append("Pick a longer user name")

            if len(errors) > 0:
                return render_template(
                    "setup.html",
                    errors=errors,
                    name=name,
                    email=email,
                    password=password,
                    state=serialize(generate_nonce()),
                )

            admin = Admins(
                name=name, email=email, password=password, type="admin", hidden=True
            )

            # Create an empty index page
            page = Pages(title=ctf_name, route="index", content="", draft=False)

            # Upload banner
            default_ctf_banner_location = url_for("views.themes", path="img/logo.png")
            ctf_banner = request.files.get("ctf_banner")
            if ctf_banner:
                f = upload_file(file=ctf_banner, page_id=page.id)
                default_ctf_banner_location = url_for("views.files", path=f.location)
                set_config("ctf_banner", f.location)

            # Splice in our banner
            index = f"""<div class="row">
    <div class="col-md-6 offset-md-3">
        <img class="w-100 mx-auto d-block" style="max-width: 500px;padding: 50px;padding-top: 14vh;" src="{default_ctf_banner_location}" />
        <h3 class="text-center">
            <p>A cool CTF platform from <a href="https://ctfd.io">ctfd.io</a></p>
            <p>Follow us on social media:</p>
            <a href="https://twitter.com/ctfdio"><i class="fab fa-twitter fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://facebook.com/ctfdio"><i class="fab fa-facebook fa-2x" aria-hidden="true"></i></a>&nbsp;
            <a href="https://github.com/ctfd"><i class="fab fa-github fa-2x" aria-hidden="true"></i></a>
        </h3>
        <br>
        <h4 class="text-center">
            <a href="admin">Click here</a> to login and setup your CTF
        </h4>
    </div>
</div>"""
            page.content = index

            # Visibility
            set_config(ConfigTypes.CHALLENGE_VISIBILITY, challenge_visibility)
            set_config(ConfigTypes.REGISTRATION_VISIBILITY, registration_visibility)
            set_config(ConfigTypes.SCORE_VISIBILITY, score_visibility)
            set_config(ConfigTypes.ACCOUNT_VISIBILITY, account_visibility)

            # Verify emails
            set_config("verify_emails", verify_emails)

            # Team Size
            set_config("team_size", team_size)

            set_config("mail_server", None)
            set_config("mail_port", None)
            set_config("mail_tls", None)
            set_config("mail_ssl", None)
            set_config("mail_username", None)
            set_config("mail_password", None)
            set_config("mail_useauth", None)

            # Set up default emails
            set_config("verification_email_subject", DEFAULT_VERIFICATION_EMAIL_SUBJECT)
            set_config("verification_email_body", DEFAULT_VERIFICATION_EMAIL_BODY)

            set_config(
                "successful_registration_email_subject",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
            )
            set_config(
                "successful_registration_email_body",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
            )

            set_config(
                "user_creation_email_subject", DEFAULT_USER_CREATION_EMAIL_SUBJECT
            )
            set_config("user_creation_email_body", DEFAULT_USER_CREATION_EMAIL_BODY)

            set_config("password_reset_subject", DEFAULT_PASSWORD_RESET_SUBJECT)
            set_config("password_reset_body", DEFAULT_PASSWORD_RESET_BODY)

            set_config(
                "password_change_alert_subject",
                "Password Change Confirmation for {ctf_name}",
            )
            set_config(
                "password_change_alert_body",
                (
                    "Your password for {ctf_name} has been changed.\n\n"
                    "If you didn't request a password change you can reset your password here: {url}"
                ),
            )

            set_config("setup", True)

            try:
                db.session.add(admin)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            try:
                db.session.add(page)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            login_user(admin)

            db.session.close()
            with app.app_context():
                cache.clear()

            return redirect(url_for("views.static_html"))
        try:
            return render_template("setup.html", state=serialize(generate_nonce()))
        except TemplateNotFound:
            # Set theme to default and try again
            set_config("ctf_theme", DEFAULT_THEME)
            return render_template("setup.html", state=serialize(generate_nonce()))
    return redirect(url_for("views.static_html"))


@views.route("/setup/integrations", methods=["GET", "POST"])
def integrations():
    if is_admin() or is_setup() is False:
        name = request.values.get("name")
        state = request.values.get("state")

        try:
            state = unserialize(state, max_age=3600)
        except (BadSignature, BadTimeSignature):
            state = False
        except Exception:
            state = False

        if state:
            if name == "mlc":
                mlc_client_id = request.values.get("mlc_client_id")
                mlc_client_secret = request.values.get("mlc_client_secret")
                set_config("oauth_client_id", mlc_client_id)
                set_config("oauth_client_secret", mlc_client_secret)
                return render_template("admin/integrations.html")
            else:
                abort(404)
        else:
            abort(403)
    else:
        abort(403)


@views.route("/notifications", methods=["GET"])
def notifications():
    notifications = Notifications.query.order_by(Notifications.id.desc()).all()
    return render_template("notifications.html", notifications=notifications)


@views.route("/settings", methods=["GET"])
@authed_only
def settings():
    infos = get_infos()
    errors = get_errors()

    user = get_current_user()

    if is_teams_mode() and get_current_team() is None:
        team_url = url_for("teams.private")
        infos.append(
            markup(
                f'In order to participate you must either <a href="{team_url}">join or create a team</a>.'
            )
        )

    tokens = UserTokens.query.filter_by(user_id=user.id).all()

    prevent_name_change = get_config("prevent_name_change")

    if get_config("verify_emails") and not user.verified:
        confirm_url = markup(url_for("auth.confirm"))
        infos.append(
            markup(
                "Your email address isn't confirmed!<br>"
                "Please check your email to confirm your email address.<br><br>"
                f'To have the confirmation email resent please <a href="{confirm_url}">click here</a>.'
            )
        )

    return render_template(
        "settings.html",
        name=user.name,
        email=user.email,
        language=user.language,
        website=user.website,
        affiliation=user.affiliation,
        country=user.country,
        tokens=tokens,
        prevent_name_change=prevent_name_change,
        infos=infos,
        errors=errors,
    )


@views.route("/", defaults={"route": "index"})
@views.route("/<path:route>")
def static_html(route):
    """
    Route in charge of routing users to Pages.
    :param route:
    :return:
    """
    page = get_page(route)
    if page is None:
        abort(404)
    else:
        if page.auth_required and authed() is False:
            return redirect(url_for("auth.login", next=request.full_path))

        return render_template("page.html", content=page.html, title=page.title)


@views.route("/tos")
def tos():
    tos_url = get_config("tos_url")
    tos_text = get_config("tos_text")
    if tos_url:
        return redirect(tos_url)
    elif tos_text:
        return render_template("page.html", content=build_markdown(tos_text))
    else:
        abort(404)


@views.route("/privacy")
def privacy():
    privacy_url = get_config("privacy_url")
    privacy_text = get_config("privacy_text")
    if privacy_url:
        return redirect(privacy_url)
    elif privacy_text:
        return render_template("page.html", content=build_markdown(privacy_text))
    else:
        abort(404)


@views.route("/files", defaults={"path": ""})
@views.route("/files/<path:path>")
def files(path):
    """
    Route in charge of dealing with making sure that CTF challenges are only accessible during the competition.
    :param path:
    :return:
    """
    f = Files.query.filter_by(location=path).first_or_404()
    if f.type == "challenge":
        if challenges_visible():
            if current_user.is_admin() is False:
                if not ctftime():
                    if ctf_ended() and view_after_ctf():
                        pass
                    else:
                        abort(403)
        else:
            # User cannot view challenges based on challenge visibility
            # e.g. ctf requires registration but user isn't authed or
            # ctf requires admin account but user isn't admin
            if not ctftime():
                # It's not CTF time. The only edge case is if the CTF is ended
                # but we have view_after_ctf enabled
                if ctf_ended() and view_after_ctf():
                    pass
                else:
                    # In all other situations we should block challenge files
                    abort(403)

            # Allow downloads if a valid token is provided
            token = request.args.get("token", "")
            try:
                data = unserialize(token, max_age=3600)
                user_id = data.get("user_id")
                team_id = data.get("team_id")
                file_id = data.get("file_id")
                user = Users.query.filter_by(id=user_id).first()
                team = Teams.query.filter_by(id=team_id).first()

                # Check user is admin if challenge_visibility is admins only
                if (
                    get_config(ConfigTypes.CHALLENGE_VISIBILITY) == "admins"
                    and user.type != "admin"
                ):
                    abort(403)

                # Check that the user exists and isn't banned
                if user:
                    if user.banned:
                        abort(403)
                else:
                    abort(403)

                # Check that the team isn't banned
                if team:
                    if team.banned:
                        abort(403)
                else:
                    pass

                # Check that the token properly refers to the file
                if file_id != f.id:
                    abort(403)

            # The token isn't expired or broken
            except (BadTimeSignature, SignatureExpired, BadSignature):
                abort(403)

    uploader = get_uploader()
    try:
        return uploader.download(f.location)
    except IOError:
        abort(404)


@views.route("/themes/<theme>/static/<path:path>")
def themes(theme, path):
    """
    General static file handler
    :param theme:
    :param path:
    :return:
    """
    for cand_path in (
        safe_join(app.root_path, "themes", cand_theme, "static", path)
        # The `theme` value passed in may not be the configured one, e.g. for
        # admin pages, so we check that first
        for cand_theme in (theme, *config.ctf_theme_candidates())
    ):
        # Handle werkzeug behavior of returning None on malicious paths
        if cand_path is None:
            abort(404)
        if os.path.isfile(cand_path):
            return send_file(cand_path, max_age=3600)
    abort(404)


@views.route("/themes/<theme>/static/<path:path>")
def themes_beta(theme, path):
    """
    This is a copy of the above themes route used to avoid
    the current appending of .dev and .min for theme assets.

    In CTFd 4.0 this url_for behavior and this themes_beta
    route will be removed.
    """
    for cand_path in (
        safe_join(app.root_path, "themes", cand_theme, "static", path)
        # The `theme` value passed in may not be the configured one, e.g. for
        # admin pages, so we check that first
        for cand_theme in (theme, *config.ctf_theme_candidates())
    ):
        # Handle werkzeug behavior of returning None on malicious paths
        if cand_path is None:
            abort(404)
        if os.path.isfile(cand_path):
            return send_file(cand_path, max_age=3600)
    abort(404)


@views.route("/healthcheck")
def healthcheck():
    if check_database() is False:
        return "ERR", 500
    if check_config() is False:
        return "ERR", 500
    return "OK", 200


@views.route("/debug")
def debug():
    if app.config.get("SAFE_MODE") is True:
        ip = get_ip()
        headers = dict(request.headers)
        # Remove Cookie item
        headers.pop("Cookie", None)
        resp = ""
        resp += f"IP: {ip}\n"
        for k, v in headers.items():
            resp += f"{k}: {v}\n"
        r = make_response(resp)
        r.mimetype = "text/plain"
        return r
    abort(404)


@views.route("/robots.txt")
def robots():
    text = get_config("robots_txt", "User-agent: *\nDisallow: /admin\n")
    r = make_response(text, 200)
    r.mimetype = "text/plain"
    return r
