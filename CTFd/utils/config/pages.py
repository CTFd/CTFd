from CTFd.cache import cache
from CTFd.models import Pages


@cache.memoize()
def get_pages():
    db_pages = Pages.query.filter(Pages.route != "index", Pages.draft != True).all()
    return db_pages


@cache.memoize()
def get_page(route):
    return Pages.query.filter(Pages.route == route, Pages.draft != True).first()
