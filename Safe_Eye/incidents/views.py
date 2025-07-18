# incidents/views.py

from rest_framework import viewsets, permissions
from .models import Incident
from .serializers import IncidentSerializer
from django_filters.rest_framework import DjangoFilterBackend

class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows incidents to be viewed or edited.
    """
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # --- ADD THIS SECTION ---
    # Enable filtering by specific fields using django-filter
    filter_backends = [DjangoFilterBackend]
    # Define the fields that can be used for filtering
    filterset_fields = ['status']
    # --- END OF SECTION ---

    def get_queryset(self):
        """
        This view should return a list of all the incidents
        for the currently authenticated user.
        """
        # It's good practice to order the results, e.g., by the most recent.
        return Incident.objects.all().order_by('-timestamp')
