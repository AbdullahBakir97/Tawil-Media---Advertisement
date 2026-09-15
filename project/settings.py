"""
Django settings for the Tawil Media project.

Configuration that differs between environments is read from environment
variables (see ``.env.example``). Nothing here should need editing to deploy.
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG = env_bool("DEBUG", default=True)

# A throwaway key is fine for local development; production must set SECRET_KEY.
SECRET_KEY = os.environ.get("SECRET_KEY") or (
    "django-insecure-local-dev-only" if DEBUG else ""
)
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set when DEBUG is off.")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
INTERNAL_IPS = ["127.0.0.1"]

SITE_NAME = "Tawil Media"
# The public origin, used for links in e-mail, where relative paths are useless.
SITE_URL = os.environ.get("SITE_URL", "")
FOUNDED_YEAR = int(os.environ.get("FOUNDED_YEAR", "2006"))

# Shown on the contact and advertise pages.
CONTACT_DETAILS = {
    "contact_email": os.environ.get("CONTACT_EMAIL", "info@tawilverlag.com"),
    "contact_phone": os.environ.get("CONTACT_PHONE", "+49 30 000 0000"),
    "company_address": {
        "street": os.environ.get("COMPANY_STREET", ""),
        "postal_code": os.environ.get("COMPANY_POSTAL_CODE", ""),
        "city": os.environ.get("COMPANY_CITY", "Berlin"),
        "country": os.environ.get("COMPANY_COUNTRY", "Germany"),
    },
}
# Director block in the home-page header. Set DIRECTOR_PHOTO to a path under static/ (e.g. "img/director.jpg").
DIRECTOR = {
    "name": os.environ.get("DIRECTOR_NAME", "Mohamad Tawil"),
    "title": os.environ.get("DIRECTOR_TITLE") or _("Founder & Creative Director"),
    "bio": os.environ.get("DIRECTOR_BIO")
    or _(
        "Leading innovation in media and advertising with over a decade of industry expertise. "
        "Committed to delivering excellence and creative solutions."
    ),
    "photo": os.environ.get("DIRECTOR_PHOTO", ""),
    "initials": "MT",
    "linkedin": os.environ.get("DIRECTOR_LINKEDIN", ""),
    "twitter": os.environ.get("DIRECTOR_TWITTER", ""),
    "stats": [
        {"key": "years", "value": "10+", "label": "Years experience"},
        {"key": "projects", "value": "500+", "label": "Projects"},
        {"key": "clients", "value": "100+", "label": "Happy clients"},
    ],
}
ADVERTISING_STATS = {"monthly_readers": "500K+", "engagement_rate": "85%", "industry_reach": "20+"}

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "taggit",
]

LOCAL_APPS = [
    "source.apps.users",
    "source.apps.core",
    "source.apps.archives",
    "source.apps.content",
    "source.apps.advertisements",
    "source.apps.subscriptions",
    "source.apps.payments",
    "source.apps.seo_analytics",
    "source.apps.newsletter",
    "source.apps.notifications",
    "source.apps.events.apps.EventsConfig",
    "source.apps.studio.apps.StudioConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Records one row per page a reader opens. Last, so it only sees responses
    # every other middleware has already finished with.
    "source.apps.seo_analytics.middleware.PageVisitMiddleware",
]

# Readership recording. Addresses are truncated before they are stored, so a
# row says "someone on this network", never "this person".
ANALYTICS_ENABLED = os.environ.get("ANALYTICS_ENABLED", "1") != "0"
ANALYTICS_RESPECT_DNT = os.environ.get("ANALYTICS_RESPECT_DNT", "1") != "0"

ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "source.apps.core.context_processors.site",
                "source.apps.notifications.context_processors.notifications",
                "source.apps.content.context_processors.header_magazines",
                "source.apps.studio.context_processors.studio",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("SQLITE_PATH", BASE_DIR / "db.sqlite3"),
    }
}

if os.environ.get("POSTGRES_DB"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ.get("POSTGRES_USER", ""),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "home"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "de"
LANGUAGES = [
    ("de", "Deutsch"),
    ("ar", "العربية"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Tawil Media <noreply@localhost>")

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------

TAGGIT_CASE_INSENSITIVE = True

# Read notifications older than this are removed by `manage.py cleanup_notifications`.
NOTIFICATION_CLEANUP_DAYS = 30

# ---------------------------------------------------------------------------
# Security (only enforced outside DEBUG)
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "source": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}
