# Safe_Eye/ai_model/urls.py

from django.urls import path
from .views import detect_accident, start_camera_detection, stop_camera_detection, get_camera_status, video_feed

urlpatterns = [
    # POST /api/ai/detect/ to run your model
    path('incident/', detect_accident, name='incident'),
    
    # MJPEG streaming endpoint
    path('video-feed/', video_feed, name='video_feed'),
    
    # Camera detection endpoints
    path('camera/start/', start_camera_detection, name='start_camera'),
    path('camera/stop/', stop_camera_detection, name='stop_camera'),
    path('camera/status/', get_camera_status, name='camera_status'),
]
