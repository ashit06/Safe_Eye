# notifications/routing.py

from django.urls import re_path
from . import consumers

# This list defines the WebSocket URL patterns for the notifications app.
websocket_urlpatterns = [
    # This route maps the URL 'ws/notifications/' to the NotificationConsumer.
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
