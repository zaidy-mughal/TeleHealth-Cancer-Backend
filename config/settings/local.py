from config.settings.base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)

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