import os

##### GENERATE SECRET KEY #####
with open('.ctfd_secret_key', 'a+') as secret:
    secret.seek(0)  # Seek to beginning of file since a+ mode leaves you at the end and w+ deletes the file
    key = secret.read()
    if not key:
        key = os.urandom(64)
        secret.write(key)
        secret.flush()

##### SERVER SETTINGS #####
SECRET_KEY = key
SQLALCHEMY_DATABASE_URI = 'sqlite:///ctfd.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds
HOST = ".ctfd.io"
UPLOAD_FOLDER = os.path.normpath('static/uploads')
TRUSTED_PROXIES = [
    '^127\.0\.0\.1$',
    ## Remove the following proxies if you do not trust the local network
    ## For example if you are running a CTF on your laptop and the teams are all on the same network
    '^::1$',
    '^fc00:',
    '^10\.',
    '^172\.(1[6-9]|2[0-9]|3[0-1])\.',
    '^192\.168\.'
]
