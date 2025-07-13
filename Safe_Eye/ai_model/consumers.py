# ai_model/consumers.py

import json
import base64
import numpy as np
import cv2
from channels.generic.websocket import WebsocketConsumer
from .camera_detection import CameraDetectionService

class DetectionConsumer(WebsocketConsumer):
    """
    WebSocket consumer with cleaner, more focused logging for debugging.
    """
    def connect(self):
        self.accept()
        print("✅ [Consumer] WebSocket connection established.")
        try:
            self.detection_service = CameraDetectionService()
            print("✅ [Consumer] CameraDetectionService initialized successfully.")
        except Exception as e:
            print(f"❌ [Consumer] FATAL: Could not initialize CameraDetectionService: {e}")

    def disconnect(self, close_code):
        print(f"❌ [Consumer] WebSocket connection closed with code: {close_code}")
        pass

    def receive(self, text_data):
        # This log confirms data is received without printing the content.
        print(f"➡️ [Consumer] Received frame from client (Size: {len(text_data)} bytes). Processing...")
        
        try:
            # Decode and process the image
            data = json.loads(text_data)
            image_data = data.get('image')
            
            if not image_data:
                print("⚠️ [Consumer] Message received but no image data found.")
                return

            header, encoded = image_data.split(",", 1)
            decoded_data = base64.b64decode(encoded)
            np_arr = np.frombuffer(decoded_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print("⚠️ [Consumer] Frame is None after decoding.")
                return

            # Call the detection service
            detections = self.detection_service.process_frame(frame)
            
            # This is the most important log. If you see this, detection was successful.
            if detections:
                print(f"✅ [Consumer] Detection successful. Found {len(detections)} objects.")
            
            # Send results back to the client
            self.send(text_data=json.dumps({
                'type': 'detections',
                'predictions': detections
            }))
        
        except Exception as e:
            # This will catch any Python-level errors during processing.
            print(f"❌ [Consumer] An unexpected error occurred in receive method: {e}")
