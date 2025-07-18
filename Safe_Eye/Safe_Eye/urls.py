# Safe_Eye/Safe_Eye/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from notifications.views import SystemSettingsViewSet
router = DefaultRouter()
# This creates the /api/settings/ and /api/settings/{id}/ endpoints
router.register(r'settings', SystemSettingsViewSet, basename='systemsettings')
api_patterns = [
    path("incidents/", include("incidents.urls")),
    path("notifications/", include("notifications.urls")),
    path("users/", include("users.urls")),
    path("ai/", include("ai_model.urls")),


    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("", include(router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: HttpResponse("✅ Safe Eye Backend is Running!")),
    path("api/", include(api_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)