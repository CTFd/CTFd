from flask import current_app

from CTFd.cache import cache
from CTFd.models import Pages, db
from CTFd.utils import get_config, markdown
from CTFd.utils.dates import isoformat, unix_time_to_utc
from CTFd.utils.formatters import safe_format
from CTFd.utils.security.sanitize import sanitize_html


def format_variables(content):
    ctf_name = get_config("ctf_name")
    ctf_description = get_config("ctf_description")
    ctf_start = get_config("start")
    if ctf_start:
        ctf_start = isoformat(unix_time_to_utc(int(ctf_start)))

    ctf_end = get_config("end")
    if ctf_end:
        ctf_end = isoformat(unix_time_to_utc(int(ctf_end)))

    ctf_freeze = get_config("freeze")
    if ctf_freeze:
        ctf_freeze = isoformat(unix_time_to_utc(int(ctf_freeze)))

    content = safe_format(
        content,
        ctf_name=ctf_name,
        ctf_description=ctf_description,
        ctf_start=ctf_start,
        ctf_end=ctf_end,
        ctf_freeze=ctf_freeze,
    )
    return content


def build_html(html, sanitize=False):
    html = format_variables(html)
    if (
        current_app.config["HTML_SANITIZATION"] is True
        or bool(get_config("html_sanitization")) is True
        or sanitize is True
    ):
        html = sanitize_html(html)
    return html


def build_markdown(md, sanitize=False):
    html = markdown(md)
    html = format_variables(html)
    if (
        current_app.config["HTML_SANITIZATION"] is True
        or bool(get_config("html_sanitization")) is True
        or sanitize is True
    ):
        html = sanitize_html(html)
    return html


@cache.memoize()
def get_pages():
    db_pages = Pages.query.filter(
        Pages.route != "index", Pages.draft.isnot(True), Pages.hidden.isnot(True)
    ).all()
    return db_pages


@cache.memoize()
def get_page(route):
    page = db.session.execute(
        Pages.__table__.select()
        .where(Pages.route == route)
        .where(Pages.draft.isnot(True))
    ).fetchone()
    if page:
        # Convert the row into a transient ORM object so this change isn't commited accidentally
        p = Pages(**page)
        return p
    return None
