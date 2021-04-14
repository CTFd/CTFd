import time

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from CTFd.config import Config

url = make_url(Config.DATABASE_URL)
url.database = None

if url.drivername.startswith('sqlite'):
    exit(0)
engine = create_engine(url)

print(f"Waiting for {url} to be ready")

while True:
    try:
        engine.raw_connection()
        break
    except Exception:
        print(".", end="", flush=True)
        time.sleep(1)

print(f"{url} is ready")
time.sleep(1)
