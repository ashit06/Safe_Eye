# notifications/views.py

from rest_framework import viewsets, permissions
from .models import Notification, SystemSettings
from .serializers import NotificationSerializer, SystemSettingsSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing notifications.
    """
    # --- CORRECTED LINE ---
    # The field name for sorting should be 'timestamp', not 'created_at'.
    queryset = Notification.objects.all().order_by('-timestamp')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

class SystemSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system-wide settings.
    This viewset handles the retrieval and update of the single settings object.
    """
    serializer_class = SystemSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This endpoint should only ever deal with the single, existing
        SystemSettings object. If it doesn't exist, it should be created.
        """
        # Use .get_or_create() to prevent errors if the settings object
        # hasn't been created in the database yet.
        settings, created = SystemSettings.objects.get_or_create(id=1)
        if created:
            # If settings were just created, you might want to log this
            # or initialize with default values.
            print("SystemSettings object created for the first time.")
        
        # Return a queryset containing only the single settings object.
        return SystemSettings.objects.filter(id=1)