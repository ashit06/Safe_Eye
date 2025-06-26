from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('incident_type', 'description', 'location', 'timestamp', 'reported_by')
    list_filter = ('incident_type', )
