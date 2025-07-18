# notifications/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    This consumer handles WebSocket connections for real-time incident notifications.
    """
    async def connect(self):
        # Define a group name that all users will join.
        # This allows us to broadcast messages to everyone connected.
        self.room_group_name = 'notifications'

        # Join the 'notifications' group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("✅ Real-time notification channel connected.")

    async def disconnect(self, close_code):
        # Leave the 'notifications' group when the connection closes.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("❌ Real-time notification channel disconnected.")

    # This method is called when a message is sent to the 'notifications' group
    # from the backend (e.g., from the incident signal).
    async def send_notification(self, event):
        message_type = event['message_type']
        incident_data = event.get('incident', {})

        # Send the message data to the connected client (the frontend).
        await self.send(text_data=json.dumps({
            'message_type': message_type,
            'incident': incident_data
        }))
