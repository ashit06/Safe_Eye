import os
import cv2
import numpy as np
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Correctly import the YOLOInference class
from .yolo_inference import YOLOInference

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detect_accident(request):
    """
    Detects accidents in an uploaded image using the shared YOLO instance.
    """
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return Response({'error': 'Invalid image file'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the shared YOLO instance and perform detection
        yolo_instance = YOLOInference.get_instance()
        detections = yolo_instance.detect_accidents(frame)

        # Format the response to be JSON friendly
        formatted_detections = [
            {'label': d.get('class_name'), 'confidence': d.get('confidence')}
            for d in detections
        ]

        return Response({
            'detections': formatted_detections,
            'total_detections': len(formatted_detections)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"❌ [API View] Error processing image: {e}")
        return Response({'error': 'An internal error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_mjpeg_stream():
    """
    Generator for the MJPEG stream, using the shared YOLO instance.
    """
    try:
        # Get the shared YOLO instance
        yolo_instance = YOLOInference.get_instance()
        
        # Check if the model inside the instance was loaded successfully
        if yolo_instance.model is None:
            print("❌ [Stream] YOLO model not loaded. Cannot start streaming.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ [Stream] Error: Could not open camera.")
            return

        while True:
            success, frame = cap.read()
            if not success:
                break

            # Use the instance's method to get the annotated frame
            annotated_frame, _ = yolo_instance.detect_and_draw(frame)

            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
            print("✅ [Stream] Camera released.")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_feed(request):
    """
    Streams live video with YOLO detection using an MJPEG stream.
    """
    return StreamingHttpResponse(
        generate_mjpeg_stream(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )