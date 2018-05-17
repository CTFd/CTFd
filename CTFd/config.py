import os

''' GENERATE SECRET KEY '''

if not os.environ.get('SECRET_KEY'):
    # Attempt to read the secret from the secret file
    # This will fail if the secret has not been written
    try:
        with open('.ctfd_secret_key', 'rb') as secret:
            key = secret.read()
    except (OSError, IOError):
        key = None

    if not key:
        key = os.urandom(64)
        # Attempt to write the secret file
        # This will fail if the filesystem is read-only
        try:
            with open('.ctfd_secret_key', 'wb') as secret:
                secret.write(key)
                secret.flush()
        except (OSError, IOError):
            pass


''' SERVER SETTINGS '''


class Config(object):
    '''
    SECRET_KEY is the secret value used to creation sessions and sign strings. This should be set to a random string. In the
    interest of ease, CTFd will automatically create a secret key file for you. If you wish to add this secret key to
    your instance you should hard code this value to a random static value.

    You can also remove .ctfd_secret_key from the .gitignore file and commit this file into whatever repository
    you are using.

    http://flask.pocoo.org/docs/0.11/quickstart/#sessions
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or key

    '''
    SQLALCHEMY_DATABASE_URI is the URI that specifies the username, password, hostname, port, and database of the server
    used to hold the CTFd database.

    http://flask-sqlalchemy.pocoo.org/2.1/config/#configuration-keys
    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{}/ctfd.db'.format(os.path.dirname(os.path.abspath(__file__)))

    '''
    SQLALCHEMY_TRACK_MODIFICATIONS is automatically disabled to suppress warnings and save memory. You should only enable
    this if you need it.
    '''
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    '''
    SESSION_TYPE is a configuration value used for Flask-Session. It is currently unused in CTFd.
    http://pythonhosted.org/Flask-Session/#configuration
    '''
    SESSION_TYPE = "filesystem"

    '''
    SESSION_FILE_DIR is a configuration value used for Flask-Session. It is currently unused in CTFd.
    http://pythonhosted.org/Flask-Session/#configuration
    '''
    SESSION_FILE_DIR = "/tmp/flask_session"

    '''
    SESSION_COOKIE_HTTPONLY controls if cookies should be set with the HttpOnly flag.
    '''
    SESSION_COOKIE_HTTPONLY = True

    '''
    PERMANENT_SESSION_LIFETIME is the lifetime of a session.
    '''
    PERMANENT_SESSION_LIFETIME = 604800  # 7 days in seconds

    '''
    HOST specifies the hostname where the CTFd instance will exist. It is currently unused.
    '''
    HOST = ".ctfd.io"

    '''
    MAILFROM_ADDR is the email address that emails are sent from if not overridden in the configuration panel.
    '''
    MAILFROM_ADDR = "noreply@ctfd.io"

    '''
    LOG_FOLDER is the location where logs are written
    These are the logs for CTFd key submissions, registrations, and logins
    The default location is the CTFd/logs folder
    '''
    LOG_FOLDER = os.environ.get('LOG_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

    '''
    UPLOAD_FOLDER is the location where files are uploaded.
    The default destination is the CTFd/uploads folder. If you need Amazon S3 files
    you can use the CTFd S3 plugin: https://github.com/ColdHeat/CTFd-S3-plugin
    '''
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    '''
    TEMPLATES_AUTO_RELOAD specifies whether Flask should check for modifications to templates and
    reload them automatically
    '''
    TEMPLATES_AUTO_RELOAD = True

    '''
    TRUSTED_PROXIES defines a set of regular expressions used for finding a user's IP address if the CTFd instance
    is behind a proxy. If you are running a CTF and users are on the same network as you, you may choose to remove
    some proxies from the list.

    CTFd only uses IP addresses for cursory tracking purposes. It is ill-advised to do anything complicated based
    solely on IP addresses.
    '''
    TRUSTED_PROXIES = [
        '^127\.0\.0\.1$',
        # Remove the following proxies if you do not trust the local network
        # For example if you are running a CTF on your laptop and the teams are all on the same network
        '^::1$',
        '^fc00:',
        '^10\.',
        '^172\.(1[6-9]|2[0-9]|3[0-1])\.',
        '^192\.168\.'
    ]

    '''
    CACHE_TYPE specifies how CTFd should cache configuration values. If CACHE_TYPE is set to 'redis', CTFd will make use
    of the REDIS_URL specified in environment variables. You can also choose to hardcode the REDIS_URL here.

    It is important that you specify some sort of cache as CTFd uses it to store values received from the database.

    CACHE_REDIS_URL is the URL to connect to Redis server.
    Example: redis://user:password@localhost:6379

    http://pythonhosted.org/Flask-Caching/#configuring-flask-caching
    '''
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    if CACHE_REDIS_URL:
        CACHE_TYPE = 'redis'
    else:
        CACHE_TYPE = 'simple'

    '''
    UPDATE_CHECK specifies whether or not CTFd will check whether or not there is a new version of CTFd
    '''
    UPDATE_CHECK = True


class TestingConfig(Config):
    SECRET_KEY = 'AAAAAAAAAAAAAAAAAAAA'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URL') or 'sqlite://'
    SERVER_NAME = 'localhost'
    UPDATE_CHECK = False
    CACHE_REDIS_URL = None
    CACHE_TYPE = 'simple'
