"""
ASGI config for mbuild project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mbuild.settings')
django_asgi_app = get_asgi_application()

from ws.consumers.edit_mode_consumer import EditModeConsumer
from ws.middlewares.jwt_auth_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter([
                path(r'edit-mode/', EditModeConsumer.as_asgi())
            ])
        )
    )
})
