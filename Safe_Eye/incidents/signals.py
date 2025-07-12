# incidents/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Incident
from notifications.models import Notification
from users.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Incident)
def create_notification_and_send_alert(sender, instance, created, **kwargs):
    if created:
        # Send email to all staff/admin users
        subject = f"[SafeEye] 🚨 New Incident Detected"
        message = f"""
An accident has been detected by the Smart Road Safety System.

Details:
- Type: {instance.incident_type}
- Description: {instance.description}
- Location: {instance.location}
- Confidence: {instance.confidence}%
- Time: {instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please take immediate action.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipients = list(CustomUser.objects.filter(is_staff=True).values_list('email', flat=True))

        if recipients:
            send_mail(subject, message, from_email, recipients, fail_silently=True)

        # Create Notification for all admins
        for user in CustomUser.objects.filter(is_staff=True):
            Notification.objects.create(
                user=user,
                incident=instance,
                message=f"New {instance.incident_type} detected at {instance.location} with confidence {instance.confidence}%",
                read=False
            )
