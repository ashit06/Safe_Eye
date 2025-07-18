# ai_model/urls.py

from django.urls import path
from . import views

# These are the specific endpoints for your AI model functionality
urlpatterns = [
    # Endpoint for uploading an image to detect an accident
    path('detect/', views.detect_accident, name='detect_accident'),
    # Endpoint for the live MJPEG video stream with detections
    path('video_feed/', views.video_feed, name='video_feed'),
]