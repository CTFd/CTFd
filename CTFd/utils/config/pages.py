from flask import current_app

from CTFd.cache import cache
from CTFd.models import Pages, db
from CTFd.utils import markdown
from CTFd.utils.security.sanitize import sanitize_html


def build_html(html):
    html = markdown(html)
    if current_app.config["HTML_SANITIZATION"] is True:
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
        p.content = build_html(p.content)
        return p
    return None
