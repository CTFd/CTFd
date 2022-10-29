import json
from flask import render_template
from flask import current_app as app
from flask import render_template, url_for

from CTFd.models import (
    UserTokens,
)

from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.decorators import authed_only
from CTFd.utils import get_config
from CTFd.utils.helpers import get_errors, get_infos, markup


# /settings view overwrite
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
    bracket = user.bracket

    verified_admin = is_admin()
    tokens = None
    if verified_admin:
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
        verified_admin=verified_admin,
        name=name,
        email=email,
        website=website,
        affiliation=affiliation,
        country=country,
        bracket=bracket,
        tokens=tokens,
        prevent_name_change=prevent_name_change,
        infos=infos,
        errors=errors,
    )
