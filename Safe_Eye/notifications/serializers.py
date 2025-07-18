# notifications/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, SystemSettings

User = get_user_model()

# This serializer is used elsewhere in your application, likely for user-related views.
# It is correctly defined and should not be removed.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# This serializer handles the conversion of individual Notification objects
# into a format that can be sent to the frontend.
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        # Using '__all__' is a convenient way to include all fields from the model.
        # This is perfectly fine for this use case.
        fields = '__all__'


# This is the key serializer for the new email notification feature.
# It allows the frontend to read and save the global alert settings.
class SystemSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the SystemSettings model.
    """
    class Meta:
        model = SystemSettings
        # Defines all the fields that can be read from or written to via the API.
        # This is what allows you to save the email address and template
        # from the "Alert Management" panel.
        fields = [
            'id',
            'email_alert_enabled',
            'sound_alert_enabled',
            'alert_email_address',
            'email_alert_template',
        ]