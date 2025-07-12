from rest_framework import viewsets
from .models import Incident
from .serializers import IncidentSerializer

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by('-timestamp')
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
