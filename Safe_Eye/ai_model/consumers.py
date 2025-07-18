import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .tasks import process_frame_task # Import the Celery task

class DetectionConsumer(AsyncWebsocketConsumer):
    """
    Asynchronous WebSocket consumer that offloads AI processing to a Celery worker
    to prevent connection timeouts.
    """
    async def connect(self):
        """
        Called when the websocket is handshaking as part of the connection process.
        """
        await self.accept()
        print("✅ [Consumer] WebSocket connection established.")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        print(f"❌ [Consumer] WebSocket connection closed with code: {close_code}")
        pass

    async def receive(self, text_data):
        """
        Receives a message from the WebSocket.
        Instead of processing the frame directly, it dispatches a background task.
        """
        try:
            data = json.loads(text_data)
            image_data = data.get('image')

            if not image_data:
                print("⚠️ [Consumer] Message received but no image data found.")
                return

            # This log confirms the handoff to the background worker.
            print(f"➡️ [Consumer] Received frame (Size: {len(text_data)} bytes). Offloading to Celery task...")

            # Trigger the background task.
            # self.channel_name is a unique identifier for this client's connection,
            # allowing the task to send the result back here later.
            process_frame_task.delay(image_data, self.channel_name)

        except json.JSONDecodeError:
            print(f"❌ [Consumer] Invalid JSON received: {text_data}")
        except Exception as e:
            # Catches any other errors during the receive process.
            print(f"❌ [Consumer] An unexpected error occurred in receive method: {e}")

    async def send_detection_results(self, event):
        """
        This is a custom handler that gets called by the Celery task
        once the AI processing is complete.
        """
        # The data from the completed task is in event['data']
        results_data = event['data']
        
        print(f"⬅️ [Consumer] Sending results back to client: {results_data}")
        
        # Send the detection results back to the original client.
        await self.send(text_data=results_data)