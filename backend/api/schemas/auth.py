from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    workspace_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    workspace_id: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    workspace_id: str
    workspace_name: str
    onboarded: bool
