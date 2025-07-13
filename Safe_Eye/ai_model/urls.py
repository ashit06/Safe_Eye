from django.urls import path
# We update the imports to only include the views that are still active.
from .views import detect_accident, video_feed

urlpatterns = [
    # This URL is for your manual image upload.
    path('incident/', detect_accident, name='incident'),
    
    # This URL is for the separate MJPEG video streaming feature.
    path('video-feed/', video_feed, name='video_feed'),
    
    # The URLs for the old camera control views have been removed to prevent import errors.
]