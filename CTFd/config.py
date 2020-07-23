import configparser
import os
from distutils.util import strtobool


def process_boolean_str(value):
    if type(value) is bool:
        return value

    if value is None:
        return False

    if value == "":
        return None

    return bool(strtobool(value))


def empty_str_cast(value, default=None):
    if value == "":
        return default
    return value


def gen_secret_key():
    # Attempt to read the secret from the secret file
    # This will fail if the secret has not been written
    try:
        with open(".ctfd_secret_key", "rb") as secret:
            key = secret.read()
    except (OSError, IOError):
        key = None

    if not key:
        key = os.urandom(64)
        # Attempt to write the secret file
        # This will fail if the filesystem is read-only
        try:
            with open(".ctfd_secret_key", "wb") as secret:
                secret.write(key)
                secret.flush()
        except (OSError, IOError):
            pass
    return key


config_ini = configparser.ConfigParser()
config_ini.optionxform = str  # Makes the key value case-insensitive
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config_ini.read(path)


# fmt: off
class ServerConfig(object):
    SECRET_KEY: str = os.getenv("SECRET_KEY") \
        or empty_str_cast(config_ini["server"]["SECRET_KEY"]) \
        or gen_secret_key()

    DATABASE_URL: str = os.getenv("DATABASE_URL") \
        or empty_str_cast(config_ini["server"]["DATABASE_URL"]) \
        or f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/ctfd.db"

    REDIS_URL: str = os.getenv("REDIS_URL") \
        or empty_str_cast(config_ini["server"]["REDIS_URL"])

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    CACHE_REDIS_URL = REDIS_URL
    if CACHE_REDIS_URL:
        CACHE_TYPE: str = "redis"
    else:
        CACHE_TYPE: str = "filesystem"
        CACHE_DIR: str = os.path.join(
            os.path.dirname(__file__), os.pardir, ".data", "filesystem_cache"
        )
        # Override the threshold of cached values on the filesystem. The default is 500. Don't change unless you know what you're doing.
        CACHE_THRESHOLD: int = 0

    # === SECURITY ===
    SESSION_COOKIE_HTTPONLY: bool = process_boolean_str(os.getenv("SESSION_COOKIE_HTTPONLY")) \
        or config_ini["security"].getboolean("SESSION_COOKIE_HTTPONLY") \
        or True

    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE") \
        or empty_str_cast(config_ini["security"]["SESSION_COOKIE_SAMESITE"]) \
        or "Lax"

    PERMANENT_SESSION_LIFETIME: int = int(os.getenv("PERMANENT_SESSION_LIFETIME", 0)) \
        or config_ini["security"].getint("PERMANENT_SESSION_LIFETIME") \
        or 604800

    """
    TRUSTED_PROXIES:
    Defines a set of regular expressions used for finding a user's IP address if the CTFd instance
    is behind a proxy. If you are running a CTF and users are on the same network as you, you may choose to remove
    some proxies from the list.

    CTFd only uses IP addresses for cursory tracking purposes. It is ill-advised to do anything complicated based
    solely on IP addresses unless you know what you are doing.
    """
    TRUSTED_PROXIES = [
        r"^127\.0\.0\.1$",
        # Remove the following proxies if you do not trust the local network
        # For example if you are running a CTF on your laptop and the teams are
        # all on the same network
        r"^::1$",
        r"^fc00:",
        r"^10\.",
        r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
        r"^192\.168\.",
    ]

    # === EMAIL ===
    MAILFROM_ADDR: str = os.getenv("MAILFROM_ADDR") \
        or config_ini["email"]["MAILFROM_ADDR"] \
        or "noreply@ctfd.io"

    MAIL_SERVER: str = os.getenv("MAIL_SERVER") \
        or empty_str_cast(config_ini["email"]["MAIL_SERVER"])

    MAIL_PORT: str = os.getenv("MAIL_PORT") \
        or empty_str_cast(config_ini["email"]["MAIL_PORT"])

    MAIL_USEAUTH: bool = process_boolean_str(os.getenv("MAIL_USEAUTH")) \
        or process_boolean_str(config_ini["email"]["MAIL_USEAUTH"])

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME") \
        or empty_str_cast(config_ini["email"]["MAIL_USERNAME"])

    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD") \
        or empty_str_cast(config_ini["email"]["MAIL_PASSWORD"])

    MAIL_TLS: bool = process_boolean_str(os.getenv("MAIL_TLS")) \
        or process_boolean_str(config_ini["email"]["MAIL_TLS"])

    MAIL_SSL: bool = process_boolean_str(os.getenv("MAIL_SSL")) \
        or process_boolean_str(config_ini["email"]["MAIL_SSL"])

    MAILGUN_API_KEY: str = os.getenv("MAILGUN_API_KEY") \
        or empty_str_cast(config_ini["email"]["MAILGUN_API_KEY"])

    MAILGUN_BASE_URL: str = os.getenv("MAILGUN_BASE_URL") \
        or empty_str_cast(config_ini["email"]["MAILGUN_API_KEY"])

    # === LOGS ===
    LOG_FOLDER: str = os.getenv("LOG_FOLDER") \
        or empty_str_cast(config_ini["logs"]["LOG_FOLDER"]) \
        or os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    # === UPLOADS ===
    UPLOAD_PROVIDER: str = os.getenv("UPLOAD_PROVIDER") \
        or empty_str_cast(config_ini["uploads"]["UPLOAD_PROVIDER"]) \
        or "filesystem"

    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER") \
        or empty_str_cast(config_ini["uploads"]["UPLOAD_FOLDER"]) \
        or os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

    if UPLOAD_PROVIDER == "s3":
        AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID") \
            or empty_str_cast(config_ini["uploads"]["AWS_ACCESS_KEY_ID"])

        AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY") \
            or empty_str_cast(config_ini["uploads"]["AWS_SECRET_ACCESS_KEY"])

        AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET") \
            or empty_str_cast(config_ini["uploads"]["AWS_S3_BUCKET"])

        AWS_S3_ENDPOINT_URL: str = os.getenv("AWS_S3_ENDPOINT_URL") \
            or empty_str_cast(config_ini["uploads"]["AWS_S3_ENDPOINT_URL"])

    # === OPTIONAL ===
    REVERSE_PROXY: bool = process_boolean_str(os.getenv("REVERSE_PROXY")) \
        or empty_str_cast(config_ini["optional"]["REVERSE_PROXY"]) \
        or False

    TEMPLATES_AUTO_RELOAD: bool = process_boolean_str(os.getenv("TEMPLATES_AUTO_RELOAD")) \
        or empty_str_cast(config_ini["optional"]["TEMPLATES_AUTO_RELOAD"]) \
        or True

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = process_boolean_str(os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")) \
        or empty_str_cast(config_ini["optional"]["SQLALCHEMY_TRACK_MODIFICATIONS"]) \
        or False

    SWAGGER_UI: bool = os.getenv("SWAGGER_UI") \
        or empty_str_cast(config_ini["optional"]["SWAGGER_UI"]) \
        or False

    SWAGGER_UI_ENDPOINT: str = "/" if SWAGGER_UI else None

    UPDATE_CHECK: bool = process_boolean_str(os.getenv("UPDATE_CHECK")) \
        or empty_str_cast(config_ini["optional"]["UPDATE_CHECK"]) \
        or True

    APPLICATION_ROOT: str = os.getenv("APPLICATION_ROOT") \
        or empty_str_cast(config_ini["optional"]["APPLICATION_ROOT"]) \
        or "/"

    SERVER_SENT_EVENTS: bool = process_boolean_str(os.getenv("SERVER_SENT_EVENTS")) \
        or empty_str_cast(config_ini["optional"]["SERVER_SENT_EVENTS"]) \
        or True

    HTML_SANITIZATION: bool = process_boolean_str(os.getenv("HTML_SANITIZATION")) \
        or empty_str_cast(config_ini["optional"]["HTML_SANITIZATION"]) \
        or False

    if DATABASE_URL.startswith("sqlite") is False:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 0))
                or int(empty_str_cast(config_ini["optional"]["SQLALCHEMY_MAX_OVERFLOW"], default=0))  # noqa: E131
                or 20,  # noqa: E131
            "pool_pre_ping": process_boolean_str(os.getenv("SQLALCHEMY_POOL_PRE_PING"))
                or empty_str_cast(config_ini["optional"]["SQLALCHEMY_POOL_PRE_PING"])  # noqa: E131
                or True,  # noqa: E131
        }

    # === OAUTH ===
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID") \
        or empty_str_cast(config_ini["oauth"]["OAUTH_CLIENT_ID"])
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET") \
        or empty_str_cast(config_ini["oauth"]["OAUTH_CLIENT_SECRET"])
# fmt: on


class TestingConfig(ServerConfig):
    SECRET_KEY = "AAAAAAAAAAAAAAAAAAAA"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TESTING_DATABASE_URL") or "sqlite://"
    SERVER_NAME = "localhost"
    UPDATE_CHECK = False
    REDIS_URL = None
    CACHE_TYPE = "simple"
    CACHE_THRESHOLD = 500
    SAFE_MODE = True


# Actually initialize ServerConfig to allow us to add more attributes on
Config = ServerConfig()
for k, v in config_ini.items("extra"):
    # Cast numeric values to their appropriate type
    if v.isdigit():
        setattr(Config, k, int(v))
    elif v.replace(".", "", 1).isdigit():
        setattr(Config, k, float(v))
    else:
        setattr(Config, k, v)
