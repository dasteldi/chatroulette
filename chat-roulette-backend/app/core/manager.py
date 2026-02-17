from fastapi import WebSocket
from typing import Dict
from datetime import datetime
from app.models.schemas import User

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, User] = {}
        self.waiting_queue: list = []
        self.active_chats: Dict[str, str] = {}
        
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.users[user_id] = User(
            id=user_id,
            name=f"User_{user_id[:4]}",
            connected_at=datetime.now()
        )
        print(f"Подключен: {user_id}")
        
    def disconnect(self, user_id: str):
        if user_id in self.waiting_queue:
            self.waiting_queue.remove(user_id)
            
        if user_id in self.active_chats:
            partner_id = self.active_chats[user_id]
            if partner_id in self.active_chats:
                del self.active_chats[partner_id]
            del self.active_chats[user_id]
            
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.users:
            del self.users[user_id]
            
        print(f"❌ Отключен: {user_id}")
        
    async def send_to_user(self, user_id: str, message: dict) -> bool:
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except:
                return False
        return False
    
    def get_online_count(self) -> int:
        return len(self.active_connections)
    
    def get_waiting_count(self) -> int:
        return len(self.waiting_queue)
    
    def get_active_chats_count(self) -> int:
        return len(self.active_chats) // 2

manager = ConnectionManager()