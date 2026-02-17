from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    connected_at: datetime

class UserCreate(BaseModel):
    name: Optional[str] = None

class UserResponse(BaseModel):
    success: bool
    data: dict

class ChatMessage(BaseModel):
    text: str
    sender: str
    sender_name: str
    timestamp: datetime = datetime.now()

class StatsResponse(BaseModel):
    success: bool
    data: dict
