from django.db import models
from django.conf import settings
from incidents.models import Incident
from solo.models import SingletonModel

# --- Existing Notification Model ---
# This model remains unchanged and will continue to function as before,
# creating specific notification entries for each admin user.
class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, 
        blank=True
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."

    class Meta:
        ordering = ['-timestamp']


# --- New System-Wide Settings Model ---
# This model is added to store the global configuration for your alert system.
# It uses SingletonModel to ensure there is only ever one row of settings.
class SystemSettings(SingletonModel):
    """
    A model to store system-wide settings, ensuring only one instance exists.
    """
    email_alert_enabled = models.BooleanField(default=True)
    sound_alert_enabled = models.BooleanField(default=True)
    
    alert_email_address = models.EmailField(
        default="admin@safe-eye.com",
        help_text="The email address where all alert notifications will be sent."
    )
    
    email_alert_template = models.TextField(
        default="""URGENT: An '{incident_type}' was detected.

Location: {location}
Time: {timestamp}
Confidence: {confidence:.2f}%

Please review the incident immediately.""",
        help_text="The template for email alerts. Use placeholders like {incident_type}, {location}, etc."
    )

    def __str__(self):
        return "System Settings"

    class Meta:
        verbose_name = "System Settings"
