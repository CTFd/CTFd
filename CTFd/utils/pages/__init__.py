from CTFd.utils import cache
from CTFd.models import Pages


@cache.memoize()
def pages():
    db_pages = Pages.query.filter(Pages.route != "index", Pages.draft != True).all()
    return db_pages


@cache.memoize()
def get_page(template):
    return Pages.query.filter(Pages.route == template, Pages.draft != True).first()