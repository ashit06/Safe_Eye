# notifications/models.py

from django.db import models
from django.conf import settings
from incidents.models import Incident

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # --- THIS IS THE FIX ---
    # We are allowing this field to be null. This solves the migration error
    # and makes sense, as some notifications might not be tied to an incident.
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
