# Safe_Eye/asgi.py

import os
from django.core.asgi import get_asgi_application

# Set the default Django settings module for the 'asgi' application.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Safe_Eye.settings')

# --- THIS IS THE FIX: Part 1 ---
# Initialize the Django application first. This is crucial because it loads
# the app registry and makes models available for other parts of the application.
django_asgi_app = get_asgi_application()

# Now that Django is initialized, we can safely import other components
# that might depend on the app registry, like routing configurations.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
import ai_model.routing
import notifications.routing

# --- THIS IS THE FIX: Part 2 ---
# The application router now uses the initialized 'django_asgi_app' for HTTP requests.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                # Combine the WebSocket URL patterns from your different apps.
                ai_model.routing.websocket_urlpatterns +
                notifications.routing.websocket_urlpatterns
            )
        )
    ),
})