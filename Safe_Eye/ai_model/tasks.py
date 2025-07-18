from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

# Corrected import to point to the right file
from .camera_detection import CameraDetectionService
from .yolo_inference import YOLOInference

@shared_task
def process_frame_task(image_data, channel_name):
    """
    Celery task to process a video frame in the background.
    """
    # Initialize the service (the model is loaded within the service)
    detection_service = CameraDetectionService()
    
    # Use the service to run detection and save the incident
    results = detection_service.process_and_save_incident(image_data)

    # Send the results back to the specific client via their channel
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        channel_name,
        {
            'type': 'send_detection_results',
            # Ensure the results dictionary is converted to a JSON string
            'data': json.dumps(results)
        }
    )
    return json.dumps(results)