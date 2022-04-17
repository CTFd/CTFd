from CTFd.models import db
from sqlalchemy.exc import OperationalError


def is_database_mariadb():
    try:
        result = db.session.execute("SELECT version()").fetchone()[0]
        mariadb = "mariadb" in result.lower()
    except OperationalError:
        mariadb = False
    return mariadb
