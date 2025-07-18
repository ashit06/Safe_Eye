import cv2
import time
import base64
import json
import numpy as np
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from incidents.models import Incident
from .yolo_inference import YOLOInference

class CameraDetectionService:
    def __init__(self):
        self.yolo = YOLOInference.get_instance()
        self.last_detection_time = 0
        # Cooldown period in seconds to prevent duplicate incident creation
        self.cooldown_period = 10 

    def process_and_save_incident(self, base64_image_string):
        try:
            # Decode the base64 image string from the WebSocket
            header, encoded = base64_image_string.split(",", 1)
            decoded_data = base64.b64decode(encoded)
            np_arr = np.frombuffer(decoded_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return {'status': 'error', 'message': 'Invalid image data'}

            # Run detection on the frame
            detections = self.yolo.detect_accidents(frame)

            # --- THE FIX IS HERE ---
            # Lowered the confidence threshold to 25% to match your model's output
            confidence_threshold = 0.25
            
            # Filter for high-confidence "accident" detections
            incident_detections = [
                d for d in detections 
                if d.get('class_name', '').lower() == 'accident' and d.get('confidence', 0) > confidence_threshold
            ]
            has_incident = bool(incident_detections)
            
            # Check if cooldown is over to avoid creating duplicate incidents
            current_time = time.time()
            is_cooldown_over = (current_time - self.last_detection_time > self.cooldown_period)

            # If an incident is detected and the cooldown is over, save it
            if has_incident and is_cooldown_over:
                self.last_detection_time = current_time  # Reset the timer
                self._handle_accident_detection(incident_detections, frame)
            
            # Prepare the results to be sent back to the client
            formatted_detections = [{'label': d.get('class_name'), 'confidence': d.get('confidence')} for d in detections]
            return {'type': 'detections', 'predictions': formatted_detections}

        except Exception as e:
            # Return a JSON response in case of an error
            return {'status': 'error', 'message': str(e)}

    def _handle_accident_detection(self, detections, frame):
        """
        Saves a new incident to the database in a single transaction.
        """
        try:
            # Use a database transaction to ensure data integrity
            with transaction.atomic():
                primary_detection = detections[0]
                
                # Encode the frame as a JPG image
                _, buffer = cv2.imencode('.jpg', frame)
                image_file_name = f"incident_{int(time.time())}.jpg"
                image_content = ContentFile(buffer.tobytes(), name=image_file_name)

                # Create and save the new Incident object
                Incident.objects.create(
                    incident_type=primary_detection.get('class_name', 'Accident').lower(),
                    description='Incident automatically detected by live camera feed.',
                    location='Live Camera Feed',  # You can enhance this later
                    confidence=primary_detection.get('confidence', 0.0),
                    image=image_content,
                    reported_by=None,  # AI-generated incidents have no user
                    status='active'
                )
        except Exception as e:
            # Log any database-related errors
            print(f"❌ [DB] FAILED to save incident. Error: {e}")



# ==============================================================================
#  ORIGINAL VIEWS AND CLASSES FOR OTHER FEATURES (UNCHANGED)
#  (Your other views like video_feed_view, detect_api, etc., remain below)
# ==============================================================================


class VideoCamera:
    """A class for the simple, local streaming view."""
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        # This now correctly uses the singleton instance
        self.yolo = YOLOInference.get_instance()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            # Use the YOLO singleton to draw boxes on the frame
            annotated_image, detections = self.yolo.detect_and_draw(image)
            # Encode the annotated image to JPEG
            ret, jpeg = cv2.imencode('.jpg', annotated_image)
            return jpeg.tobytes(), detections
        return None, []

def gen(camera):
    """Generator function for the streaming response."""
    while True:
        frame, _ = camera.get_frame()
        if frame:
            # Yield the frame in the multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed_view(request):
    """A view for a simple multipart video stream."""
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def detect_api(request):
    """A view for handling manual image uploads via a REST API endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            # Decode the base64 image from the API request
            _, imgstr = image_data.split(';base64,')
            image_bytes = base64.b64decode(imgstr)

            # Convert the bytes to a NumPy array for OpenCV
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # This also correctly uses the singleton instance now
            yolo = YOLOInference.get_instance()
            annotated_image, detections = yolo.detect_and_draw(img)

            # Encode the annotated image back to base64 to send in the JSON response
            _, buffer = cv2.imencode('.jpg', annotated_image)
            annotated_image_b64 = base64.b64encode(buffer).decode('utf-8')

            return JsonResponse({
                'detections': detections,
                'annotated_image': f"data:image/jpeg;base64,{annotated_image_b64}"
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def index(request):
    """Renders a simple index page."""
    return render(request, 'camera/index.html')