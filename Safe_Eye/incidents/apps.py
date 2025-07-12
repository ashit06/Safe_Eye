from django.apps import AppConfig


class IncidentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incidents'

    def ready(self):
        # Import the signals module to ensure the signal handlers are registered
        import incidents.signals


