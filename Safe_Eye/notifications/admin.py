# notifications/admin.py

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """
    
    # --- THIS IS THE FIX ---
    # The field name has been corrected from 'is_read' to 'read'.
    list_display = ('user', 'incident', 'message', 'timestamp', 'read')
    
    # The filter has also been corrected from 'is_read' to 'read'.
    list_filter = ('read', 'timestamp')
    
    search_fields = ('user__username', 'message', 'incident__description')
    
    # Make the 'read' field editable directly from the list view
    list_editable = ('read',)
    
    # Order by most recent first
    ordering = ('-timestamp',)

