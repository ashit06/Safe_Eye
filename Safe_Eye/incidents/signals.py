# incidents/signals.py

from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Incident
from .serializers import IncidentSerializer
from notifications.models import Notification
from notifications.tasks import send_incident_email_task

def trigger_background_tasks(instance):
    """
    This helper function contains the tasks that should only run AFTER the
    database transaction is successfully committed.
    """
    # --- Task 1: Trigger Asynchronous Email Alert ---
    print(f"✅ Transaction committed. Triggering email alert task for incident ID: {instance.id}")
    send_incident_email_task.delay(instance.id)

    # --- Task 2: Send Real-Time WebSocket Notification ---
    channel_layer = get_channel_layer()
    
    # To use the serializer's context and build full URLs for images,
    # we create a dummy request object.
    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/')
    
    serializer = IncidentSerializer(instance, context={'request': Request(request)})
    incident_data = serializer.data

    # Send the message to the 'notifications' channel group
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "send_notification",
            "message_type": "new_incident_alert",
            "incident": incident_data
        }
    )
    print(f"✅ Sent real-time WebSocket notification for incident ID: {instance.id}")


@receiver(post_save, sender=Incident)
def incident_post_save_handler(sender, instance, created, **kwargs):
    """
    Signal handler that runs immediately after an Incident is saved.
    """
    if created:
        # --- Action 1: Create DB Notification for Admins (This can run immediately) ---
        User = get_user_model()
        admin_users = User.objects.filter(is_staff=True)
        
        for user in admin_users:
            Notification.objects.create(
                user=user,
                incident=instance,
                message=f"New '{instance.incident_type}' detected at {instance.location}."
            )
        print(f"✅ Created {admin_users.count()} database notifications for incident ID: {instance.id}")

        # --- THIS IS THE FIX ---
        # Defer the background tasks (Celery, Channels) until the transaction is committed.
        # This prevents the race condition where the worker can't find the incident.
        transaction.on_commit(lambda: trigger_background_tasks(instance))
