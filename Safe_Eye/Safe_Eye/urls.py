from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: HttpResponse("Safe Eye Backend is Running 🚀")),
    path('api/', include('users.urls')),
    path('api/', include('incidents.urls')),
    path('api/', include('notifications.urls')),
    path('api/ai/', include('ai_model.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
