from config.settings.base import *
import dj_database_url
import os


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['.railway.app', '*']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if not os.getenv('DATABASE_URL'):
    raise Exception('DATABASE_URL environment variable is required in production!')

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Add whitenoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
