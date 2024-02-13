import os

import environ
import sentry_sdk

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, "abcedf132987401747501873"),
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
environ.Env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))
DEBUG = env("DEBUG")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
# For development purposes, set DEBUG to True in a local_settings.py file,
# which we .gitignore. This file should be added in the same directory
# that contains this settings.py file.

SECRET_KEY = env("SECRET_KEY")

db_path = "/data/prod.sqlite3"
if DEBUG:
    db_path = os.path.join(BASE_DIR, "db.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": db_path,  # Or path to database file if using sqlite3.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
APP_NAME = env("FLY_APP_NAME", str, "")
ALLOWED_HOSTS = [f"{APP_NAME}.fly.dev", "vote.electionscience.org"]  # ← Updated!
if DEBUG:
    ALLOWED_HOSTS.extend(["localhost", "0.0.0.0"])

CSRF_TRUSTED_ORIGINS = ["https://vote.electionscience.org"]
CSRF_ALLOWED_ORIGINS = ["https://vote.electionscience.org"]
CORS_ORIGINS_WHITELIST = ["https://vote.electionscience.org"]

# The following settings are required for the activation emails in the
# registration module to work.
SENDGRID_API_KEY = env("SENDGRID_API_KEY", str, default="")
if SENDGRID_API_KEY != "":
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
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

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "staticfiles/"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

LOGIN_REDIRECT_URL = "/"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_ajax.middleware.AJAXMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allauth.account.middleware.AccountMiddleware",
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
)

ACCOUNT_ACTIVATION_DAYS = 7

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
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
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTHENTICATION_BACKENDS = [
    "approval_polls.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]  # Change your authentication backend

FIDO_SERVER_ID = "vote.electionscience.org"  # Server rp id for FIDO2, it the full domain of your project
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

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = env(
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL", str, default="https"
)


sentry_sdk.init(
    dsn="https://78856604267db99554868743d5eb61e5@o4506681396625408.ingest.sentry.io/4506681396756480",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
