from django.db import models
from django.conf import settings

class Incident(models.Model):
    incident_type = models.CharField(max_length=20, default='Accident')
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True  # allow null for AI-generated detections
    )
    confidence = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='incidents/', null=True, blank=True)

    def __str__(self):
        return f"Accident at {self.location or 'Unknown'}"
