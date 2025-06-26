from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'incident', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read',)
