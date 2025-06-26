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
from .camera_detection import camera_service

# Import YOLO and set up model for streaming
try:
    from ultralytics import YOLO
    import torch
    from torch.serialization import add_safe_globals
    from ultralytics.nn.tasks import DetectionModel
    
    # Add safe globals for YOLO model loading
    add_safe_globals([DetectionModel])
    
    # Load the YOLO model for streaming
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, 'best.pt')
    
    model = None
    try:
        model = YOLO(MODEL_PATH)
        print("YOLO model loaded successfully for streaming")
    except Exception as e:
        print(f"Error loading YOLO model for streaming: {e}")
        # Fallback: try loading with weights_only=False
        try:
            import torch.serialization
            original_weights_only = torch.serialization._weights_only
            torch.serialization._weights_only = False
            model = YOLO(MODEL_PATH)
            torch.serialization._weights_only = original_weights_only
            print("YOLO model loaded with fallback method")
        except Exception as e2:
            print(f"Failed to load YOLO model for streaming: {e2}")
            model = None

except ImportError as e:
    print(f"Failed to import YOLO dependencies: {e}")
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
        # Run prediction
        results = predict_image(temp_path)
        
        # Process results into a clean format
        detections = []
        if results and len(results) > 0:
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get class and confidence
                        cls = int(box.cls[0].cpu().numpy())
                        conf = float(box.conf[0].cpu().numpy())
                        
                        # Get class name
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
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def generate_mjpeg_stream():
    """Generate MJPEG stream with YOLO detection and bounding boxes"""
    if model is None:
        print("Error: YOLO model not loaded. Cannot start streaming.")
        return
    
    cap = cv2.VideoCapture(0)  # Use default camera (index 0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("Error: Could not read frame")
                break
            
            # Run YOLO inference on the frame
            results = model(frame, conf=0.5)  # Confidence threshold of 0.5
            
            # Draw bounding boxes and labels on the frame
            annotated_frame = results[0].plot()
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield the frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    except Exception as e:
        print(f"Error in MJPEG stream: {e}")
    
    finally:
        cap.release()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_feed(request):
    """Stream live video with YOLO detection"""
    if model is None:
        return Response({'error': 'YOLO model not loaded'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        return StreamingHttpResponse(
            generate_mjpeg_stream(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Legacy camera detection endpoints for backward compatibility
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_camera_detection(request):
    """Start camera detection service (legacy endpoint)"""
    try:
        # Get parameters from request
        camera_source = request.data.get('camera_source', 0)
        detection_interval = float(request.data.get('detection_interval', 1.0))
        
        # Start camera detection
        camera_service.start_camera_detection(
            camera_source=int(camera_source),
            detection_interval=detection_interval
        )
        
        return Response({
            'status': 'success',
            'message': f'Camera detection started on source {camera_source}',
            'camera_source': camera_source,
            'detection_interval': detection_interval
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_camera_detection(request):
    """Stop camera detection service (legacy endpoint)"""
    try:
        camera_service.stop_camera_detection()
        return Response({
            'status': 'success',
            'message': 'Camera detection stopped'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_camera_status(request):
    """Get camera detection status (legacy endpoint)"""
    try:
        status = camera_service.get_camera_status()
        return Response(status)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
