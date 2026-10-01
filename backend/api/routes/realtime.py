import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from backend.api.realtime.websocket_manager import ws_manager
from backend.api.auth import SECRET_KEY, ALGORITHM
from backend.api.database import SessionLocal
from backend.api.models import Workspace

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Wait for the first message to be authentication
        auth_msg_text = await websocket.receive_text()
        auth_msg = json.loads(auth_msg_text)
        if auth_msg.get("type") != "authenticate":
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        token = auth_msg.get("token")
        if not token:
            await websocket.close(code=1008, reason="Token required")
            return
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token subject")
        except (JWTError, ValueError):
            await websocket.close(code=1008, reason="Invalid token")
            return
            
        # Resolve workspace
        with SessionLocal() as db:
            workspace = db.query(Workspace).filter(Workspace.owner_id == user_id).first()
            if not workspace:
                await websocket.close(code=1008, reason="No workspace found")
                return
            workspace_id = workspace.id

        await ws_manager.connect(websocket, workspace_id)
        
        while True:
            data = await websocket.receive_text()
            # Ignore further incoming messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

