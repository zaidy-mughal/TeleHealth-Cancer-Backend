"""
WSGI config for project.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from config.setup_environment import setup_environment

print("Starting WSGI application...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    setup_environment()
    print("Environment setup complete")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    print(f"Using settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

    application = get_wsgi_application()
    print("WSGI application initialized successfully")
except Exception as e:
    print(f"Error initializing WSGI application: {str(e)}")
    raise
