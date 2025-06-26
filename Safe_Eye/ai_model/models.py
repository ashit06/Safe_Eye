from django.db import models
from django.http import JsonResponse

class CameraFeed(models.Model):
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    stream_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.location
    
def detect_accident(request):
    return JsonResponse({'message': 'AI model will process here'})
