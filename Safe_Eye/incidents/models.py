from django.db import models
from django.conf import settings

class Incident(models.Model):
    """
    Represents a detected incident.
    """
    # --- THIS IS THE FIX ---
    # Define choices for the new status field.
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
    ]

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
    
    # Add the missing 'status' field.
    # It will default to 'active' for all new incidents created by the AI.
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    # --- END OF FIX ---

    def __str__(self):
        return f"{self.incident_type} at {self.location or 'Unknown'} ({self.status})"
