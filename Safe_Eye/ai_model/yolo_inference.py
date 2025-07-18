# ai_model/yolo_inference.py

import os
from ultralytics import YOLO

class YOLOInference:
    """
    A singleton class to manage the YOLO model.
    This ensures the model is loaded into memory only once and shared.
    """
    _instance = None  # This class variable will hold the single instance

    @classmethod
    def get_instance(cls):
        """
        This is the correct way to get the YOLO model instance.
        It creates a new one only if it doesn't exist.
        """
        if cls._instance is None:
            print("🧠 [YOLO] No instance found. Creating new YOLOInference instance...")
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        The constructor is now 'private'. It loads the model when the
        first instance is created by get_instance().
        """
        # This check prevents anyone from creating a new instance directly
        if hasattr(YOLOInference, '_instance') and YOLOInference._instance is not None:
            raise Exception("This is a singleton class. Use YOLOInference.get_instance() to access it.")

        try:
            # Construct the full path to the model file
            model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
            print(f"🧠 [YOLO] Loading model from: {model_path}")
            self.model = YOLO(model_path)
            print("✅ [YOLO] Model loaded successfully.")
        except Exception as e:
            print(f"❌ [YOLO] FATAL: Could not load model. Error: {e}")
            self.model = None

    def detect_accidents(self, frame):
        """
        Runs accident detection on a given frame and returns structured data.
        """
        if not self.model:
            return [] # Return empty list if model failed to load

        # verbose=False keeps the console clean during detection
        results = self.model(frame, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'class_name': self.model.names[int(box.cls)],
                    'confidence': float(box.conf)
                })
        return detections

    def detect_and_draw(self, frame):
        """
        This method runs detection and draws the bounding boxes on the image.
        It's used by your other, non-WebSocket views.
        """
        if not self.model:
            return frame, []

        results = self.model(frame, verbose=False)
        # .plot() is a helper from Ultralytics to draw the boxes
        annotated_frame = results[0].plot()
        # We can reuse the main detection logic
        detections = self.detect_accidents(frame)
        return annotated_frame, detections