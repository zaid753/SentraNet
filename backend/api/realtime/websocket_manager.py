import asyncio
import logging
from typing import Dict
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from backend.api.events import event_bus, EventEnvelope, EventTypes

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, bool] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = True
        
        # Send initial connection event
        await self.send_event(websocket, EventEnvelope(
            event_type=EventTypes.SYSTEM_STATUS_CHANGED,
            payload={"status": "CONNECTED", "message": "WebSocket connected successfully."}
        ))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    async def send_event(self, websocket: WebSocket, event: EventEnvelope):
        if websocket.application_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(event.model_dump_json())
            except Exception as e:
                logger.error(f"Error sending event to WebSocket: {e}")
                self.disconnect(websocket)

    async def broadcast(self, event: EventEnvelope):
        # We need a copy of the keys to avoid dictionary changed size during iteration
        for connection in list(self.active_connections.keys()):
            await self.send_event(connection, event)

ws_manager = WebSocketManager()

async def ws_event_handler(event: EventEnvelope):
    """
    Subscriber handler that forwards events from the EventBus to the WebSocketManager.
    """
    await ws_manager.broadcast(event)

# Subscribe to all events
event_bus.subscribe_all(ws_event_handler)
