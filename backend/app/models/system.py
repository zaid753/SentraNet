from pydantic import BaseModel

class ComponentStatus(BaseModel):
    status: str

class SystemStatus(BaseModel):
    backend: ComponentStatus
    database: ComponentStatus
    ml_models: ComponentStatus
    replay_engine: ComponentStatus
    websocket: ComponentStatus
