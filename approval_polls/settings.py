import os
import sys

import environ
import sentry_sdk
import structlog

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "abcedf132987401747501873"),
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))
DEBUG = env("DEBUG")
print("Debug?: ", DEBUG)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
# For development purposes, set DEBUG to True in a local_settings.py file,
# which we .gitignore. This file should be added in the same directory
# that contains this settings.py file.

SECRET_KEY = env("SECRET_KEY")

db_path = "/data/prod.sqlite3"

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
APP_NAME = env("FLY_APP_NAME", str, "")
ALLOWED_HOSTS = [f"{APP_NAME}.fly.dev", "vote.electionscience.org"]  # ← Updated!
print("Allowed Hosts: ", ALLOWED_HOSTS)
print("APP_NAME: ", APP_NAME)

if DEBUG:
    db_path = os.path.join(BASE_DIR, "db.sqlite3")
    ALLOWED_HOSTS.extend(["localhost", "0.0.0.0", "127.0.0.1"])  # trunk-ignore(bandit)


if not DEBUG:
    COMPRESS_OFFLINE = True
    LIBSASS_OUTPUT_STYLE = "compressed"

    def filter_invalid_host_errors(event, hint):
        """Filter out invalid HTTP_HOST header errors from Sentry."""
        # Check exception type in hint
        if "exc_info" in hint:
            exc_type, exc_value, tb = hint["exc_info"]
            if exc_type.__name__ == "DisallowedHost":
                return None
        # Check log record message
        if "log_record" in hint:
            msg = str(hint.get("log_record", {}).get("msg", ""))
            if "Invalid HTTP_HOST header" in msg:
                return None
        # Check event exception data directly
        if event.get("exception"):
            for exc in event["exception"].get("values", []):
                exc_type = exc.get("type", "")
                exc_value = exc.get("value", "")
                if (
                    exc_type == "DisallowedHost"
                    or "Invalid HTTP_HOST header" in exc_value
                ):
                    return None
        return event

    sentry_sdk.init(
        dsn="https://78856604267db99554868743d5eb61e5@o4506681396625408.ingest.sentry.io/4506681396756480",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        before_send=filter_invalid_host_errors,
    )
    CSRF_TRUSTED_ORIGINS = [
        "https://vote.electionscience.org",
        f"https://{APP_NAME}.fly.dev",
    ]
    CSRF_ALLOWED_ORIGINS = [
        "https://vote.electionscience.org",
        f"https://{APP_NAME}.fly.dev",
    ]
    CORS_ORIGINS_WHITELIST = [
        "https://vote.electionscience.org",
        f"https://{APP_NAME}.fly.dev",
    ]


if "test" in sys.argv or "pytest" in sys.argv:
    COMPRESS_OFFLINE = False
    COMPRESS_ENABLED = False

DATABASES = {
    "default": {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": db_path,  # Or path to database file if using sqlite3.
    }
}


# The following settings are required for the activation emails in the
# registration module to work.
MAILGUN_API_KEY = env("MAILGUN_API_KEY", str, default="")
MAILGUN_DOMAIN = env(
    "MAILGUN_DOMAIN", str, default="sandbox6fd6a89cd7964a43823dad8cc15226b1.mailgun.org"
)

if MAILGUN_API_KEY != "":
    # Use Mailgun API backend
    EMAIL_BACKEND = "approval_polls.mailgun_backend.MailgunBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "vote@electionscience.org"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "staticfiles/"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

LOGIN_REDIRECT_URL = "/"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE = (
    "django_structlog.middlewares.RequestMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_ajax.middleware.AJAXMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

ROOT_URLCONF = "approval_polls.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "approval_polls.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    "approval_polls",
    "django_extensions",
    "django_ajax",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "widget_tweaks",
    "import_export",
    "compressor",
)

ACCOUNT_ACTIVATION_DAYS = 7

# Structlog configuration for structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "approval_polls": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = [
    "approval_polls.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]  # Change your authentication backend

# Server rp id for FIDO2, it the full domain of your project
FIDO_SERVER_ID = "vote.electionscience.org"
FIDO_SERVER_NAME = "vote.electionscience.org"
if DEBUG:
    FIDO_SERVER_ID = (
        "localhost"  # Server rp id for FIDO2, it the full domain of your project
    )
    FIDO_SERVER_NAME = "localhost"

KEY_ATTACHMENT = None


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        "APP": {
            "client_id": "766775776124-db3o7dn963di14rteuue1hkeg1hmh1mv.apps.googleusercontent.com",
            "secret": env("GOOGLE_SECRET", str, default=""),
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
    }
}

ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*"]
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env(
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL", str, default="https"
)
