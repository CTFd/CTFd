from CTFd.cache import cache
from CTFd.models import db, Pages


@cache.memoize()
def get_pages():
    db_pages = Pages.query.filter(
        Pages.route != "index", Pages.draft.isnot(True), Pages.hidden.isnot(True)
    ).all()
    return db_pages


@cache.memoize()
def get_page(route):
    return db.session.execute(
        Pages.__table__.select()
        .where(Pages.route == route)
        .where(Pages.draft.isnot(True))
    ).fetchone()
