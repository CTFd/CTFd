import os
import time

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from CTFd.config import Config

url = make_url(Config.DATABASE_URL)
if not url.drivername.startswith("mysql"):
    exit(0)

engine = create_engine(url)
print(f"Waiting for {url.host}:{url.port or 3306} to be ready")

while True:
    try:
        engine.raw_connection().ping()
        print()
        break
    except:
        print('.', end='', flush=True)
        time.sleep(1)

print(f"{url.host}:{url.port or 3306} is ready")
time.sleep(1)
