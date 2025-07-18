# notifications/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import SystemSettings
from incidents.models import Incident

@shared_task
def send_incident_email_task(incident_id):
    """
    A Celery task to send an email notification for a new incident.
    This version is corrected to handle template formatting errors.
    """
    try:
        # Retrieve the single instance of system settings.
        system_settings = SystemSettings.get_solo()
        incident = Incident.objects.get(id=incident_id)

        if not system_settings.email_alert_enabled:
            print(f"Email alerts are disabled. Skipping email for incident {incident_id}.")
            return

        recipient_email = system_settings.alert_email_address
        if not recipient_email:
            print(f"No recipient email address is configured. Skipping email for incident {incident_id}.")
            return

        subject = f"🚨 Alert: {incident.incident_type.capitalize()} Detected"
        template = system_settings.email_alert_template

        # Prepare the context dictionary with values that are always present.
        context = {
            'incident_type': incident.incident_type.capitalize(),
            'location': incident.location or "Unknown Location",
            'timestamp': incident.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'description': incident.description or "No description provided."
        }

        # --- THIS IS THE FIX ---
        # We now handle the confidence value carefully to avoid formatting errors.
        if incident.confidence is not None:
            # If confidence exists, add it to the context as a number.
            # The template can now safely use {confidence:.2f} or {confidence}.
            context['confidence'] = incident.confidence * 100
            message = template.format(**context)
        else:
            # If confidence is None, we cannot use a template that expects a number.
            # We must manually replace the placeholder with "N/A" first.
            # This handles both {confidence:.2f}% and {confidence}.
            message_intermediate = template.replace("{confidence:.2f}%", "N/A")
            message_intermediate = message_intermediate.replace("{confidence}", "N/A")
            # Now, format the rest of the placeholders.
            message = message_intermediate.format(**context)
        # --- END OF FIX ---
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        print(f"✅ Successfully sent email alert for incident {incident_id} to {recipient_email}")

    except SystemSettings.DoesNotExist:
        print("System settings not found. Cannot send email.")
    except Incident.DoesNotExist:
        print(f"Incident with ID {incident_id} not found. Cannot send email.")
    except Exception as e:
        print(f"❌ Failed to send incident email: {e}")