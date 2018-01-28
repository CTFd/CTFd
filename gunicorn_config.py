import multiprocessing
import os
import base64

# http://docs.gunicorn.org/en/stable/settings.html
# https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py

bind='0.0.0.0:8000'

# Worker settings
worker_class='gevent'
worker=2*multiprocessing.cpu_count()

# Logging settings
loglevel='info'
accesslog=os.path.join(os.environ['LOG_FOLDER'], 'access.log')
errorlog=os.path.join(os.environ['LOG_FOLDER'], 'error.log')

# Reload on code changes. Useful for development
reload=True
# poll consumes more resources than inotify, but is more compatible
reload_engine='poll'

# SSL
# For development, you can generate a self-signed cert with:
#   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./ssl/ctfd.key -out ./ssl/ctfd.crt
# For production, check out Let's Encrypt for free certificates https://letsencrypt.org/
ssl_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssl') # Not a gunicorn setting
if os.path.isdir(ssl_dir):
    keyfile=os.path.join(ssl_dir, 'ctfd.key')
    certfile=os.path.join(ssl_dir, 'ctfd.crt')

# Set the database url for CTFd
os.environ['DATABASE_URL']='mysql+pymysql://root:{MYSQL_ROOT_PASSWORD}@db/ctfd'.format(**os.environ)

# Because the code is mounted read-only. Generate a new SECRET_KEY if one does not exist
if not os.environ.get('SECRET_KEY'):
    try:
        secret_key_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.ctfd_secret_key') # Not a gunicorn setting
        with open(secret_key_file, 'rb') as f:
            os.environ['SECRET_KEY'] = base64.b32encode(f.read()).decode('utf-8')
    except OSError:
        os.environ['SECRET_KEY'] = base64.b32encode(os.urandom(64)).decode('utf-8')
