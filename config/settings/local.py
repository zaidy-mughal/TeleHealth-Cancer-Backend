from config.settings.base import *


# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = env("DEBUG", default=True)
DEBUG = True

ALLOWED_HOSTS = ["*"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "telehealth_db"),
        "USER": os.getenv("POSTGRES_USER", "telehealth_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "telehealth_pass"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

REST_AUTH.update(
    {
        "JWT_AUTH_SECURE": False,
        "JWT_AUTH_SAMESITE": "None",
    }
)

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
