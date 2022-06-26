"""
WSGI config for django_boilerplate project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from config.setup_environment import setup_environment

setup_environment()

application = get_wsgi_application()
