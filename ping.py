import time

from sqlalchemy.engine.url import make_url

from CTFd.config import Config

url = make_url(Config.DATABASE_URL)
url.database = None


class PingError(Exception):
    pass


def mysql_ping(**kwargs):
    """this imitates `mysqladmin ping`"""
    from pymysql import Error, connect
    try:
        connect(**kwargs).ping()
    except Error:
        raise PingError()


def postgres_ping(**kwargs):
    """NotImplemented"""


print(f"Waiting for {url} to be ready")

while True:
    try:
        if url.drivername.startswith("mysql"):
            mysql_ping(
                host=url.host,
                user=url.username,
                password=url.password,
                port=url.port,
                database=None,
            )
        elif url.drivername.startswith("postgres"):
            postgres_ping()
        print()
        break
    except PingError:
        print(".", end="", flush=True)
        time.sleep(1)

print(f"{url} is ready")
time.sleep(1)
