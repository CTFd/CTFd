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
    """
    CTFd Configuration Object
    """

    '''
    === REQUIRED SETTINGS ===

    SECRET_KEY:
        The secret value used to creation sessions and sign strings. This should be set to a random string. In the
        interest of ease, CTFd will automatically create a secret key file for you. If you wish to add this secret key
        to your instance you should hard code this value to a random static value.

        You can also remove .ctfd_secret_key from the .gitignore file and commit this file into whatever repository
        you are using.

        http://flask.pocoo.org/docs/latest/quickstart/#sessions

    SQLALCHEMY_DATABASE_URI:
        The URI that specifies the username, password, hostname, port, and database of the server
        used to hold the CTFd database.

        e.g. mysql+pymysql://root:<YOUR_PASSWORD_HERE>@localhost/ctfd

    CACHE_TYPE:
        Specifies how CTFd should cache configuration values. If CACHE_TYPE is set to 'redis', CTFd will make use
        of the REDIS_URL specified in environment variables. You can also choose to hardcode the REDIS_URL here.

        It is important that you specify some sort of cache as CTFd uses it to store values received from the database. If
        no cache is specified, CTFd will default to a simple per-worker cache. The simple cache cannot be effectively used
        with multiple workers.

    REDIS_URL is the URL to connect to a Redis server.
        e.g. redis://user:password@localhost:6379
        http://pythonhosted.org/Flask-Caching/#configuring-flask-caching
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or key
    DATABASE_URL = os.environ.get(
        'DATABASE_URL') or 'sqlite:///{}/ctfd.db'.format(os.path.dirname(os.path.abspath(__file__)))
    REDIS_URL = os.environ.get('REDIS_URL')

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or REDIS_URL
    if CACHE_REDIS_URL:
        CACHE_TYPE = 'redis'
    else:
        CACHE_TYPE = 'filesystem'
        CACHE_DIR = os.path.join(os.path.dirname(
            __file__), os.pardir, '.data', 'filesystem_cache')

    '''
    === SECURITY ===

    SESSION_COOKIE_HTTPONLY:
        Controls if cookies should be set with the HttpOnly flag.

    PERMANENT_SESSION_LIFETIME:
        The lifetime of a session. The default is 604800 seconds.

    TRUSTED_PROXIES:
        Defines a set of regular expressions used for finding a user's IP address if the CTFd instance
        is behind a proxy. If you are running a CTF and users are on the same network as you, you may choose to remove
        some proxies from the list.

        CTFd only uses IP addresses for cursory tracking purposes. It is ill-advised to do anything complicated based
        solely on IP addresses unless you know what you are doing.
    '''
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 604800  # 7 days in seconds
    TRUSTED_PROXIES = [
        r'^127\.0\.0\.1$',
        # Remove the following proxies if you do not trust the local network
        # For example if you are running a CTF on your laptop and the teams are
        # all on the same network
        r'^::1$',
        r'^fc00:',
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
        r'^192\.168\.'
    ]

    '''
    === EMAIL ===

    MAILFROM_ADDR:
        The email address that emails are sent from if not overridden in the configuration panel.

    MAIL_SERVER:
        The mail server that emails are sent from if not overriden in the configuration panel.

    MAIL_PORT:
        The mail port that emails are sent from if not overriden in the configuration panel.
    '''
    MAILFROM_ADDR = "noreply@ctfd.io"
    MAIL_SERVER = None
    MAIL_PORT = None
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_TLS = False
    MAIL_SSL = False
    MAILGUN_API_KEY = None
    MAILGUN_BASE_URL = None

    '''
    === LOGS ===
    LOG_FOLDER:
        The location where logs are written. These are the logs for CTFd key submissions, registrations, and logins.
        The default location is the CTFd/logs folder.
    '''
    LOG_FOLDER = os.environ.get('LOG_FOLDER') or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'logs')

    '''
    === UPLOADS ===

    UPLOAD_PROVIDER:
        Specifies the service that CTFd should use to store files.

    UPLOAD_FOLDER:
        The location where files are uploaded. The default destination is the CTFd/uploads folder.

    AWS_ACCESS_KEY_ID:
        AWS access token used to authenticate to the S3 bucket.

    AWS_SECRET_ACCESS_KEY:
        AWS secret token used to authenticate to the S3 bucket.

    AWS_S3_BUCKET:
        The unique identifier for your S3 bucket.

    AWS_S3_ENDPOINT_URL:
        A URL pointing to a custom S3 implementation.

    '''
    UPLOAD_PROVIDER = os.environ.get('UPLOAD_PROVIDER') or 'filesystem'
    if UPLOAD_PROVIDER == 'filesystem':
        UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or \
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    elif UPLOAD_PROVIDER == 's3':
        AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or ''
        AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or ''
        AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET') or ''
        AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL') or ''

    '''
    === OPTIONAL ===

    REVERSE_PROXY:
        Specifies whether CTFd is behind a reverse proxy or not. Set to True if using a reverse proxy like nginx.

    TEMPLATES_AUTO_RELOAD:
        Specifies whether Flask should check for modifications to templates and reload them automatically.

    SQLALCHEMY_TRACK_MODIFICATIONS:
        Automatically disabled to suppress warnings and save memory. You should only enable this if you need it.

    UPDATE_CHECK:
        Specifies whether or not CTFd will check whether or not there is a new version of CTFd

    APPLICATION_ROOT:
        Specifies what path CTFd is mounted under. It can be used to run CTFd in a subdirectory.
        Example: /ctfd
    '''
    REVERSE_PROXY = False
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPDATE_CHECK = True
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT') or '/'

    '''
    === OAUTH ===

    MajorLeagueCyber Integration
        Register an event at https://majorleaguecyber.org/ and use the Client ID and Client Secret here
    '''
    OAUTH_CLIENT_ID = None
    OAUTH_CLIENT_SECRET = None


class TestingConfig(Config):
    SECRET_KEY = 'AAAAAAAAAAAAAAAAAAAA'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URL') or 'sqlite://'
    SERVER_NAME = 'localhost'
    UPDATE_CHECK = False
    REDIS_URL = None
    CACHE_TYPE = 'simple'
