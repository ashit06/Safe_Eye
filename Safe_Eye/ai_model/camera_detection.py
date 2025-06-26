import cv2
import threading
import time
import os
from ultralytics import YOLO
from django.conf import settings
import requests
import json

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
        """
        Run YOLO detection on a frame
        
        Args:
            frame: OpenCV frame
            
        Returns:
            List of detections with bounding boxes and confidence scores
        """
        try:
            results = self.model(frame)
            detections = []
            
            for result in results:
                for box in result.boxes:
                    detection = {
                        'class': int(box.cls),
                        'label': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'box': [float(coord) for coord in box.xyxy[0]],
                        'timestamp': time.time()
                    }
                    detections.append(detection)
                    
            return detections
            
        except Exception as e:
            print(f"❌ Error in accident detection: {e}")
            return []
            
    def _handle_accident_detection(self, detections, frame):
        """
        Handle detected accidents - save to database, notify frontend, etc.
        
        Args:
            detections: List of detected objects
            frame: The frame where detection occurred
        """
        try:
            # Save frame as image (optional)
            timestamp = int(time.time())
            frame_path = f"media/accident_frames/accident_{timestamp}.jpg"
            os.makedirs(os.path.dirname(frame_path), exist_ok=True)
            cv2.imwrite(frame_path, frame)
            
            # Create incident record in database
            incident_data = {
                'incident_type': 'accident',
                'detections': detections,
                'frame_path': frame_path,
                'timestamp': timestamp,
                'camera_id': 'live_camera'
            }
            
            # Call Django API to save incident
            self._save_incident_to_database(incident_data)
            
            print(f"📸 Accident frame saved: {frame_path}")
            
        except Exception as e:
            print(f"❌ Error handling accident detection: {e}")
            
    def _save_incident_to_database(self, incident_data):
        """
        Save incident to Django database via API call
        """
        try:
            # This would call your Django API endpoint
            # For now, we'll just print the data
            print(f"💾 Saving incident to database: {incident_data}")
            
            # TODO: Implement actual API call to save incident
            # response = requests.post(
            #     'http://127.0.0.1:8000/api/incidents/',
            #     json=incident_data,
            #     headers={'Content-Type': 'application/json'}
            # )
            
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