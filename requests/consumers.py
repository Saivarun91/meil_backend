from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.request_id = self.scope['url_route']['kwargs']['request_id']
            self.group_name = f"chat_{self.request_id}"

            # Join room group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send connection confirmation
            await self.send(text_data=json.dumps({
                "type": "system",
                "message": "connected",
                "request_id": self.request_id
            }))
            
            logger.info(f"WebSocket connected for request {self.request_id}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected for request {self.request_id}")
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                data = json.loads(text_data)
                if data.get("type") == "ping":
                    await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")

    async def chat_message(self, event):
        """
        Handler for chat.message events from channel layer
        This method is called when a message is broadcast to the group
        """
        try:
            message_data = event.get("message", {})
            await self.send(text_data=json.dumps({
                "type": "chat",
                "message": message_data,
            }))
            logger.debug(f"Chat message sent to WebSocket for request {self.request_id}")
        except Exception as e:
            logger.error(f"Error sending chat message: {e}")




