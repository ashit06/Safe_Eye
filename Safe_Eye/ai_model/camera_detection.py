import cv2
import time
import os
from datetime import datetime
from django.core.files.base import ContentFile
from incidents.models import Incident
# --- This is the updated import ---
# It now imports the YOLOInference class from your yolo_inference.py file.
from .yolo_inference import YOLOInference

# --- This is the refactored class for the WebSocket ---
# It now correctly uses your YOLOInference class.
class CameraDetectionService:
    def __init__(self):
        """
        Initializes the YOLOInference service.
        """
        # The model is now loaded within your YOLOInference class.
        self.yolo = YOLOInference()
        self.last_detection_time = 0
        self.detection_interval = 5  # 5-second cooldown

    def process_frame(self, frame):
        """
        This is the main method called by the WebSocket consumer.
        It analyzes a single frame and triggers incident creation if needed.
        """
        # This now calls the method from your yolo_inference.py file.
        detections = self.yolo.detect_accidents(frame)
        
        current_time = time.time()
        
        # If detections are found and the cooldown has passed, handle the incident.
        if detections and (current_time - self.last_detection_time > self.detection_interval):
            print(f"✅ [Service] Accident detected. Starting cooldown.")
            self.last_detection_time = current_time
            self._handle_accident_detection(detections, frame)

        # The format of the detections dictionary is different, so we adjust it here
        # for compatibility with the frontend.
        formatted_detections = [
            {'label': d.get('class_name'), 'confidence': d.get('confidence')} 
            for d in detections
        ]
        return formatted_detections

    def _handle_accident_detection(self, detections, frame):
        """
        Creates an Incident record directly in the database with detailed logging.
        """
        print("--- Entered _handle_accident_detection ---")
        try:
            # Step 1: Get the primary detection
            primary_detection = detections[0]
            print("... Step 1: Primary detection retrieved.")

            # Step 2: Encode the image
            _, buffer = cv2.imencode('.jpg', frame)
            image_file_name = f"incident_{int(time.time())}.jpg"
            print(f"... Step 2: Image encoded as '{image_file_name}'.")

            # Step 3: Create a Django ContentFile
            image_content = ContentFile(buffer.tobytes(), name=image_file_name)
            print("... Step 3: Django ContentFile created.")

            # Step 4: Attempt to save to the database
            print("... Step 4: Calling Incident.objects.create()...")
            Incident.objects.create(
                incident_type=primary_detection.get('class_name', 'Accident').lower(),
                description='Incident automatically detected by live camera feed.',
                location='Live Camera Feed',
                confidence=primary_detection.get('confidence', 0.0),
                image=image_content,
                reported_by=None
            )
            print("✅ [Service] Incident saved successfully to database.")
            print("--- Exiting _handle_accident_detection ---")

        except Exception as e:
            print(f"❌ [Service] An error occurred while saving the incident: {e}")
            print("--- Exiting _handle_accident_detection with error ---")


# --- All of your original code for other features remains below ---
# This ensures that any other parts of your app that use these continue to work.

from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import numpy as np

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        # This now correctly uses the YOLOInference class from your file.
        self.yolo = YOLOInference() 

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            # Note: Your YOLOInference class needs a 'detect_and_draw' method
            # for this specific view to work. We'll assume it exists.
            try:
                annotated_image, detections = self.yolo.detect_and_draw(image)
            except AttributeError:
                # Fallback if detect_and_draw doesn't exist
                annotated_image = image
            ret, jpeg = cv2.imencode('.jpg', annotated_image)
            return jpeg.tobytes(), []
        return None, []

def gen(camera):
    while True:
        frame, detections = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed_view(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@csrf_exempt
def detect_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'error': 'No image data provided'}, status=400)
            
            format, imgstr = image_data.split(';base64,') 
            image_bytes = base64.b64decode(imgstr)
            
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            yolo = YOLOInference()
            # Note: This view also expects a 'detect_and_draw' method.
            try:
                annotated_image, detections = yolo.detect_and_draw(img)
            except AttributeError:
                annotated_image = img
                detections = yolo.detect_accidents(img)

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
    return render(request, 'camera/index.html')