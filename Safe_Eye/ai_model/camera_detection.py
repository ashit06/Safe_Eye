import cv2
import threading
import time
import os
from ultralytics import YOLO
from django.conf import settings
import requests
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from django.core.files.base import ContentFile
from incidents.models import Incident

class CameraDetectionService:
    def __init__(self):
        # Get the directory of the current script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, 'best.pt')
        
        # Load the YOLO model
        self.model = YOLO(MODEL_PATH)
        self.is_running = False
        self.camera_thread = None
        self.camera = None
        
    def start_camera_detection(self, camera_source=0, detection_interval=1.0):
        """
        Start live camera detection
        
        Args:
            camera_source: Camera source (0 for default webcam, or IP camera URL)
            detection_interval: How often to run detection (in seconds)
        """
        if self.is_running:
            print("Camera detection is already running!")
            return
            
        self.is_running = True
        self.camera_thread = threading.Thread(
            target=self._camera_detection_loop,
            args=(camera_source, detection_interval)
        )
        self.camera_thread.daemon = True
        self.camera_thread.start()
        print(f"🎥 Camera detection started on source: {camera_source}")
        
    def stop_camera_detection(self):
        """Stop live camera detection"""
        self.is_running = False
        if self.camera:
            self.camera.release()
        if self.camera_thread:
            self.camera_thread.join()
        print("🛑 Camera detection stopped")
        
    def _camera_detection_loop(self, camera_source, detection_interval):
        """Main camera detection loop"""
        try:
            # Open camera
            self.camera = cv2.VideoCapture(camera_source)
            
            if not self.camera.isOpened():
                print(f"❌ Error: Could not open camera source {camera_source}")
                return
                
            print(f"📹 Camera opened successfully: {camera_source}")
            
            last_detection_time = 0
            
            while self.is_running:
                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Error reading frame from camera")
                    break
                    
                current_time = time.time()
                
                # Run detection at specified interval
                if current_time - last_detection_time >= detection_interval:
                    detections = self._detect_accidents(frame)
                    print(f"👀 Raw detections: {detections}")  # 🔍 This line helps verify output

                    if detections:
                        print(f"🚨 Accident detected! Found {len(detections)} incidents")
                        self._handle_accident_detection(detections, frame)

                    last_detection_time = current_time

                    
                # Optional: Display live feed (comment out for production)
                # cv2.imshow('Live Camera Detection', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                    
        except Exception as e:
            print(f"❌ Error in camera detection loop: {e}")
        finally:
            if self.camera:
                self.camera.release()
            cv2.destroyAllWindows()
            
    def _detect_accidents(self, frame):
        try:
            results = self.model(frame)[0]  # Only first result
            detections = []

            for box in results.boxes:
                cls_id = int(box.cls.item())
                label = self.model.names[cls_id]
                conf = float(box.conf.item())
                coords = box.xyxy[0].tolist()

                detection = {
                    'class': cls_id,
                    'label': label,
                    'confidence': conf,
                    'box': coords,
                    'timestamp': time.time()
                }
                detections.append(detection)

            print(f"👀 Raw detections: {detections}")
            return detections

        except Exception as e:
            print(f"❌ Error in accident detection: {e}")
            return []


    from datetime import datetime

    def _handle_accident_detection(self, detections, frame):
        """
        Creates an Incident record directly in the database.
        This is more secure and efficient than making an API call to itself.
        """
        print(f"🧠 _handle_accident_detection triggered with {len(detections)} detections.")
        try:
            primary_detection = detections[0]

            _, buffer = cv2.imencode('.jpg', frame)
            image_file_name = f"incident_{int(time.time())}.jpg"
            image_content = ContentFile(buffer.tobytes(), name=image_file_name)

            Incident.objects.create(
                incident_type=primary_detection.get('label', 'Accident').lower(),
                description='Incident automatically detected by live camera feed.',
                location='Live Camera Feed',
                confidence=primary_detection.get('confidence', 0.0),
                image=image_content,
                reported_by=None
            )
            print(f"✅ Incident saved directly to the database with image {image_file_name}.")
        except Exception as e:
            print(f"❌ Error while saving incident directly to database: {e}")



    def _save_incident_to_database(self, incident_data):
        try:
            print("🔐 Logging in as admin...")

            # Step 1: Login to get token
            auth_response = requests.post(
                "http://127.0.0.1:8000/api/token/",
                json={"username": "admin", "password": "admin123"},
                headers={"Content-Type": "application/json"}
            )

            if auth_response.status_code != 200:
                print("❌ Failed to authenticate admin")
                print(auth_response.text)
                return

            access_token = auth_response.json().get("access")

            # Step 2: Extract file and data
            files = {
                'image': incident_data['image']
            }
            data = {
                'incident_type': incident_data['incident_type'],
                'description': incident_data['description'],
                'location': incident_data['location'],
                'confidence': incident_data['confidence'],
            }

            print("📨 Sending POST to /api/incidents/ ...")

            response = requests.post(
                "http://127.0.0.1:8000/api/incidents/",
                data=data,
                files=files,
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )

            if response.status_code == 201:
                print("✅ Incident saved to database")
            else:
                print(f"❌ Failed to save incident: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ Error saving incident to database: {e}")



            
    def get_camera_status(self):
        """Get current camera detection status"""
        return {
            'is_running': self.is_running,
            'camera_source': getattr(self, 'camera_source', None),
            'detection_interval': getattr(self, 'detection_interval', None)
        }

# Global instance
camera_service = CameraDetectionService() 