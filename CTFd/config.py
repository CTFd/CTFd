import os
##### SERVER SETTINGS #####
SECRET_KEY = os.urandom(64)
SQLALCHEMY_DATABASE_URI = 'sqlite:///ctfd.db'
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
HOST = ".ctfd.io"
UPLOAD_FOLDER = os.path.normpath('static/uploads')

##### EMAIL #####
CTF_NAME = ''
MAIL_SERVER = ''
MAIL_PORT = 0
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
ADMINS = []
