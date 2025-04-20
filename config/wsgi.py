"""
WSGI config for django_boilerplate project.
"""

import os
from django.core.wsgi import get_wsgi_application
from config.setup_environment import setup_environment

setup_environment()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()