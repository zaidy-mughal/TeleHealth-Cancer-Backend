"""
ASGI config for TELEHEALTH project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

from config.setup_environment import setup_environment

setup_environment()

application = get_asgi_application()
