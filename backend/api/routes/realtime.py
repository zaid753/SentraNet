import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.api.realtime.websocket_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await ws_manager.connect(websocket)
        
        while True:
            data = await websocket.receive_text()
            # Ignore further incoming messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

