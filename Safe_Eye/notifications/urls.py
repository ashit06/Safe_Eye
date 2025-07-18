# notifications/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# We only need the NotificationViewSet here now.
from .views import NotificationViewSet

router = DefaultRouter()

# Register the NotificationViewSet under an empty prefix.
# This will correctly create the /api/notifications/ endpoint.
router.register('', NotificationViewSet, basename='notification')

# The SystemSettingsViewSet has been moved to the main urls.py to avoid
# creating an incorrect nested URL like /api/notifications/settings/.

urlpatterns = [
    # This includes all the registered routes from the router above.
    path('', include(router.urls)),
]
