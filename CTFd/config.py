import os
##### SERVER SETTINGS #####
SECRET_KEY = os.urandom(64)
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/ctfd'
SQLALCHEMY_DATABASE_URI = 'sqlite:///ctfd.db'
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds
HOST = ".ctfd.io"
UPLOAD_FOLDER = os.path.normpath('static/uploads')

##### EMAIL (Mailgun and non-Mailgun) #####

# The first address will be used as the from address of messages sent from CTFd
ADMINS = []

##### EMAIL (if not using Mailgun) #####
CTF_NAME = ''
MAIL_SERVER = ''
MAIL_PORT = 0
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
