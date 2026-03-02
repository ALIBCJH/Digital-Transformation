# CI settings for GitHub Actions
# Uses SQLite to avoid PostgreSQL extension dependencies

from .settings import *  # noqa: F403, F401

# Use SQLite for CI to avoid PostgreSQL extension issues
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Flag to conditionally disable problematic indexes
USE_ADVANCED_POSTGRES_FEATURES = False

# Disable features that require PostgreSQL
USE_POSTGRES_EXTENSIONS = False

# Additional CI optimizations
DEBUG = False
SECRET_KEY = "test-secret-key-for-ci-only-do-not-use-in-production"
ALLOWED_HOSTS = ["*"]

# Speed up tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging to speed up tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
    },
}
