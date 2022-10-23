import json
from flask import render_template
from flask import current_app as app
from flask import redirect, render_template, request, send_file, session, url_for

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

from CTFd.utils.user import authed, get_current_team, get_current_user, is_admin

from CTFd import utils
from CTFd.utils.decorators import authed_only
from CTFd.utils import config, get_config, set_config
from CTFd.utils.helpers import get_errors, get_infos, markup


def load(app):
    app.view_functions['views.settings'] = view_settings

@authed_only
def view_settings():
    infos = get_infos()
    errors = get_errors()

    user = get_current_user()
    name = user.name
    email = user.email
    website = user.website
    affiliation = user.affiliation
    country = user.country
    app.logger.info(user.__dict__)

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
        csaw_team_members=json.dumps([{'name': 'Alex Aaron', 'email': 'aa@alexaroncontact.com', 'school': 'Arizona State University'}]),
        name=name,
        email=email,
        website=website,
        affiliation=affiliation,
        country=country,
        tokens=tokens,
        prevent_name_change=prevent_name_change,
        infos=infos,
        errors=errors,
    )