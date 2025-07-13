# Safe_Eye/asgi.py
"""
ASGI config for Safe_Eye project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set the settings module environment variable.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Safe_Eye.settings')

# This is the critical line that configures Django's settings.
django.setup()

# Now that Django is configured, we can safely import other parts of the app.
from channels.auth import AuthMiddlewareStack
from ai_model.routing import websocket_urlpatterns


application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": get_asgi_application(),

    # WebSocket chat handler
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})