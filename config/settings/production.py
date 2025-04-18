from config.settings.base import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: update this with your domain
ALLOWED_HOSTS = ['*']  # Update this with your actual domain in production

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres:postgres@localhost:5432/telehealth',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS_ALLOWED_ORIGINS = cors_origins.split(',') if cors_origins else []
CORS_ALLOW_CREDENTIALS = True

# Add trusted origins for CSRF
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# For development, you can also allow all origins (remove in production)
CORS_ALLOW_ALL_ORIGINS = True  # Remove this line when you have a frontend
