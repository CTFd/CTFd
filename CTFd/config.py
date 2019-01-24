import os

''' GENERATE SECRET KEY '''

if not os.getenv('SECRET_KEY'):
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
    SECRET_KEY = os.getenv('SECRET_KEY') or key
    DATABASE_URL = os.getenv('DATABASE_URL') or 'sqlite:///{}/ctfd.db'.format(os.path.dirname(os.path.abspath(__file__)))
    REDIS_URL = os.getenv('REDIS_URL')

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    CACHE_REDIS_URL = REDIS_URL
    if CACHE_REDIS_URL:
        CACHE_TYPE = 'redis'
    else:
        CACHE_TYPE = 'filesystem'
        CACHE_DIR = os.path.join(os.path.dirname(__file__), os.pardir, '.data', 'filesystem_cache')
        CACHE_THRESHOLD = 0  # Override the threshold of cached values on the filesystem. The default is 500. Don't change unless you know what you're doing.

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
    SESSION_COOKIE_HTTPONLY = (not os.getenv("SESSION_COOKIE_HTTPONLY"))  # Defaults True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE") or 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME") or 604800)  # 7 days in seconds
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

    MAIL_USEAUTH
        Whether or not to use username and password to authenticate to the SMTP server

    MAIL_USERNAME
        The username used to authenticate to the SMTP server if MAIL_USEAUTH is defined

    MAIL_PASSWORD
        The password used to authenticate to the SMTP server if MAIL_USEAUTH is defined

    MAIL_TLS
        Whether to connect to the SMTP server over TLS

    MAIL_SSL
        Whether to connect to the SMTP server over SSL

    MAILGUN_API_KEY
        Mailgun API key to send email over Mailgun

    MAILGUN_BASE_URL
        Mailgun base url to send email over Mailgun
    '''
    MAILFROM_ADDR = os.getenv("MAILFROM_ADDR") or "noreply@ctfd.io"
    MAIL_SERVER = os.getenv("MAIL_SERVER") or None
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USEAUTH = os.getenv("MAIL_USEAUTH")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_TLS = os.getenv("MAIL_TLS") or False
    MAIL_SSL = os.getenv("MAIL_SSL") or False
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_BASE_URL = os.getenv("MAILGUN_BASE_URL")

    '''
    === LOGS ===
    LOG_FOLDER:
        The location where logs are written. These are the logs for CTFd key submissions, registrations, and logins.
        The default location is the CTFd/logs folder.
    '''
    LOG_FOLDER = os.getenv('LOG_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

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
    UPLOAD_PROVIDER = os.getenv('UPLOAD_PROVIDER') or 'filesystem'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    if UPLOAD_PROVIDER == 's3':
        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
        AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')

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

    SOCKETIO_ASYNC_MODE:
        Specifies what async mode SocketIO should use.
        Specifying your own async mode is not recommended without the appropriate load balancing mechanisms
        in place and proper understanding of how websockets are supported by Flask.
        https://flask-socketio.readthedocs.io/en/latest/#deployment
    '''
    REVERSE_PROXY = os.getenv("REVERSE_PROXY") or False
    TEMPLATES_AUTO_RELOAD = (not os.getenv("TEMPLATES_AUTO_RELOAD"))  # Defaults True
    SQLALCHEMY_TRACK_MODIFICATIONS = (not os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"))  # Defaults True
    UPDATE_CHECK = (not os.getenv("UPDATE_CHECK"))  # Defaults True
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT') or '/'
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE')

    '''
    === OAUTH ===

    MajorLeagueCyber Integration
        Register an event at https://majorleaguecyber.org/ and use the Client ID and Client Secret here
    '''
    OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")


class TestingConfig(Config):
    SECRET_KEY = 'AAAAAAAAAAAAAAAAAAAA'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TESTING_DATABASE_URL') or 'sqlite://'
    SERVER_NAME = 'localhost'
    UPDATE_CHECK = False
    REDIS_URL = None
    CACHE_TYPE = 'simple'
    CACHE_THRESHOLD = 500
    SAFE_MODE = True
