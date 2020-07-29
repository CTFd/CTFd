import configparser
import os
from distutils.util import strtobool


class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        envvar = os.getenv(option)
        if value == "" and envvar:
            return process_string_var(envvar)
        else:
            return value


def process_string_var(value):
    if value == "":
        return None

    if value.isdigit():
        return int(value)
    elif value.replace(".", "", 1).isdigit():
        return float(value)

    try:
        return bool(strtobool(value))
    except ValueError:
        return value


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


config_ini = configparser.ConfigParser(interpolation=EnvInterpolation())
config_ini.optionxform = str  # Makes the key value case-insensitive
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config_ini.read(path)


# fmt: off
class ServerConfig(object):
    SECRET_KEY: str = empty_str_cast(config_ini["server"]["SECRET_KEY"]) \
        or gen_secret_key()

    DATABASE_URL: str = empty_str_cast(config_ini["server"]["DATABASE_URL"]) \
        or f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/ctfd.db"

    REDIS_URL: str = empty_str_cast(config_ini["server"]["REDIS_URL"])

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
    SESSION_COOKIE_HTTPONLY: bool = config_ini["security"].getboolean("SESSION_COOKIE_HTTPONLY") \
        or True

    SESSION_COOKIE_SAMESITE: str = empty_str_cast(config_ini["security"]["SESSION_COOKIE_SAMESITE"]) \
        or "Lax"

    PERMANENT_SESSION_LIFETIME: int = config_ini["security"].getint("PERMANENT_SESSION_LIFETIME") \
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
    MAILFROM_ADDR: str = config_ini["email"]["MAILFROM_ADDR"] \
        or "noreply@ctfd.io"

    MAIL_SERVER: str = empty_str_cast(config_ini["email"]["MAIL_SERVER"])

    MAIL_PORT: int = empty_str_cast(config_ini["email"]["MAIL_PORT"])

    MAIL_USEAUTH: bool = process_boolean_str(config_ini["email"]["MAIL_USEAUTH"])

    MAIL_USERNAME: str = empty_str_cast(config_ini["email"]["MAIL_USERNAME"])

    MAIL_PASSWORD: str = empty_str_cast(config_ini["email"]["MAIL_PASSWORD"])

    MAIL_TLS: bool = process_boolean_str(config_ini["email"]["MAIL_TLS"])

    MAIL_SSL: bool = process_boolean_str(config_ini["email"]["MAIL_SSL"])

    MAILGUN_API_KEY: str = empty_str_cast(config_ini["email"]["MAILGUN_API_KEY"])

    MAILGUN_BASE_URL: str = empty_str_cast(config_ini["email"]["MAILGUN_API_KEY"])

    # === LOGS ===
    LOG_FOLDER: str = empty_str_cast(config_ini["logs"]["LOG_FOLDER"]) \
        or os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

    # === UPLOADS ===
    UPLOAD_PROVIDER: str = empty_str_cast(config_ini["uploads"]["UPLOAD_PROVIDER"]) \
        or "filesystem"

    UPLOAD_FOLDER: str = empty_str_cast(config_ini["uploads"]["UPLOAD_FOLDER"]) \
        or os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

    if UPLOAD_PROVIDER == "s3":
        AWS_ACCESS_KEY_ID: str = empty_str_cast(config_ini["uploads"]["AWS_ACCESS_KEY_ID"])

        AWS_SECRET_ACCESS_KEY: str = empty_str_cast(config_ini["uploads"]["AWS_SECRET_ACCESS_KEY"])

        AWS_S3_BUCKET: str = empty_str_cast(config_ini["uploads"]["AWS_S3_BUCKET"])

        AWS_S3_ENDPOINT_URL: str = empty_str_cast(config_ini["uploads"]["AWS_S3_ENDPOINT_URL"])

    # === OPTIONAL ===
    REVERSE_PROXY: bool = empty_str_cast(config_ini["optional"]["REVERSE_PROXY"]) \
        or False

    TEMPLATES_AUTO_RELOAD: bool = empty_str_cast(config_ini["optional"]["TEMPLATES_AUTO_RELOAD"]) \
        or True

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = empty_str_cast(config_ini["optional"]["SQLALCHEMY_TRACK_MODIFICATIONS"]) \
        or False

    SWAGGER_UI: bool = empty_str_cast(config_ini["optional"]["SWAGGER_UI"]) \
        or False

    SWAGGER_UI_ENDPOINT: str = "/" if SWAGGER_UI else None

    UPDATE_CHECK: bool = empty_str_cast(config_ini["optional"]["UPDATE_CHECK"]) \
        or True

    APPLICATION_ROOT: str = empty_str_cast(config_ini["optional"]["APPLICATION_ROOT"]) \
        or "/"

    SERVER_SENT_EVENTS: bool = empty_str_cast(config_ini["optional"]["SERVER_SENT_EVENTS"]) \
        or True

    HTML_SANITIZATION: bool = empty_str_cast(config_ini["optional"]["HTML_SANITIZATION"]) \
        or False

    if DATABASE_URL.startswith("sqlite") is False:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "max_overflow": int(empty_str_cast(config_ini["optional"]["SQLALCHEMY_MAX_OVERFLOW"], default=0))  # noqa: E131
                or 20,  # noqa: E131
            "pool_pre_ping": empty_str_cast(config_ini["optional"]["SQLALCHEMY_POOL_PRE_PING"])  # noqa: E131
                or True,  # noqa: E131
        }

    # === OAUTH ===
    OAUTH_CLIENT_ID: str = empty_str_cast(config_ini["oauth"]["OAUTH_CLIENT_ID"])
    OAUTH_CLIENT_SECRET: str = empty_str_cast(config_ini["oauth"]["OAUTH_CLIENT_SECRET"])
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
    setattr(Config, k, process_string_var(v))
