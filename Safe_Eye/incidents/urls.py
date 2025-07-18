# incidents/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentViewSet

# The router automatically generates the standard list and detail endpoints.
router = DefaultRouter()

# By registering with an empty prefix (""), the URLs generated will be based on
# the prefix from the main urls.py file.
# This correctly creates /api/incidents/ and /api/incidents/{id}/.
router.register("", IncidentViewSet, basename="incident")

urlpatterns = [
    path("", include(router.urls)),
]
