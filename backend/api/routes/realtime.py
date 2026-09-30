import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.api.realtime import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # We don't really expect client to send us data in Phase 4, but we must keep the connection open
            # and receive messages to know if they disconnect.
            data = await websocket.receive_text()
            # We can just ignore incoming messages for now
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
