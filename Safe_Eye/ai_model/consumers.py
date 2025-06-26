import json
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from .yolo_inference import YOLOInference
import logging

logger = logging.getLogger(__name__)

class DetectionConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yolo_model = YOLOInference()

    async def connect(self):
        await self.accept()
        logger.info("WebSocket connected")
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket connected and YOLO model loaded'
        }))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            # You can still handle manual commands if needed
            logger.info(f"Received text_data: {data}")

        elif bytes_data:
            logger.info("Received frame from frontend")
            try:
                nparr = np.frombuffer(bytes_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is None:
                    logger.error("Invalid frame received (decode failed)")
                    return

                detections = self.yolo_model.detect_accidents(frame)
                
                # Send detections back to frontend
                await self.send(text_data=json.dumps({
                    "type": "detections",
                    "detections": detections
                }))

            except Exception as e:
                logger.exception(f"Error processing frame: {e}")
