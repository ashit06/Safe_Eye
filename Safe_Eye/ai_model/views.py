import os
import json
import cv2
import numpy as np
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .yolo_inference import predict_image
# We no longer import 'camera_service' as it has been removed.

# Import YOLO and set up model for streaming
try:
    from ultralytics import YOLO
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, 'best.pt')
    
    model = YOLO(MODEL_PATH)
    print("YOLO model loaded successfully for streaming")

except ImportError as e:
    print(f"Failed to import YOLO dependencies: {e}")
    model = None
except Exception as e:
    print(f"Failed to load YOLO model for streaming: {e}")
    model = None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detect_accident(request):
    """Detect accidents in uploaded image"""
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = request.FILES['image']
    
    # Save the uploaded image temporarily
    temp_path = f'/tmp/uploaded_image_{image_file.name}'
    with open(temp_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    
    try:
        results = predict_image(temp_path)
        
        detections = []
        if results and len(results) > 0:
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        conf = float(box.conf[0].cpu().numpy())
                        class_name = result.names[cls]
                        
                        detections.append({
                            'label': class_name,
                            'confidence': conf,
                            'box': [float(x1), float(y1), float(x2), float(y2)]
                        })
        
        return Response({
            'detections': detections,
            'total_detections': len(detections)
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def generate_mjpeg_stream():
    """Generate MJPEG stream with YOLO detection and bounding boxes"""
    if model is None:
        print("Error: YOLO model not loaded. Cannot start streaming.")
        return
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            results = model(frame, conf=0.5)
            annotated_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    finally:
        cap.release()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_feed(request):
    """Stream live video with YOLO detection"""
    if model is None:
        return Response({'error': 'YOLO model not loaded'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return StreamingHttpResponse(
        generate_mjpeg_stream(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

# --- The views below are now obsolete and have been commented out to prevent errors ---
# --- Their functionality is now handled by the WebSocket consumer ---

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def start_camera_detection(request):
#     """Start camera detection service (legacy endpoint)"""
#     # This logic is now handled by the WebSocket connection.
#     return JsonResponse({'status': 'This endpoint is deprecated.'})

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def stop_camera_detection(request):
#     """Stop camera detection service (legacy endpoint)"""
#     # This logic is now handled by the WebSocket connection.
#     return JsonResponse({'status': 'This endpoint is deprecated.'})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_camera_status(request):
#     """Get camera detection status (legacy endpoint)"""
#     return JsonResponse({'status': 'This endpoint is deprecated.'})