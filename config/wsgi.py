"""
WSGI config for django_boilerplate project.
"""

import os
from django.core.wsgi import get_wsgi_application
from config.setup_environment import setup_environment

setup_environment()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Force production settings in Railway
if os.getenv('RAILWAY_ENVIRONMENT_NAME'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    os.environ['APP_ENVIRONMENT'] = 'production'
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

application = get_wsgi_application()