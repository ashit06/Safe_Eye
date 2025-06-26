from ultralytics import YOLO
import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'best.pt')

model = None
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    # Fallback: try loading with weights_only=False
    try:
        import torch.serialization
        original_weights_only = torch.serialization._weights_only
        torch.serialization._weights_only = False
        model = YOLO(MODEL_PATH)
        torch.serialization._weights_only = original_weights_only
    except Exception as e2:
        print(f"Failed to load YOLO model with fallback: {e2}")
        model = None

class YOLOInference:
    def __init__(self):
        global model
        self.model = model
        if self.model is None:
            raise RuntimeError("YOLO model not loaded.")

    def detect_accidents(self, img):
        """
        Accept numpy frame directly
        """
        results = self.model(img)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id] if hasattr(self.model, 'names') else str(class_id)
                detections.append({
                    'bbox': bbox,
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
        return detections
    
    # For backward-compatibility with your REST “manual upload” view
def predict_image(image_path: str):
    """
    Load an image from disk path, run YOLO inference, return raw results list.
    """
    if model is None:
        raise RuntimeError("YOLO model not loaded.")
    return model(image_path)




