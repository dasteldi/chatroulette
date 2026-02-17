from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
import string
from typing import Dict
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.users: Dict[str, dict] = {}
        self.waiting_queue = []
        self.active_chats = {}
        
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.users[user_id] = {
            "name": f"User_{user_id[:4]}",
            "connected_at": datetime.now().isoformat()
        }
        print(f"✅ Подключен: {user_id}")
        
    def disconnect(self, user_id: str):
        # Удаляем из очереди
        if user_id in self.waiting_queue:
            self.waiting_queue.remove(user_id)
            
        # Удаляем из чатов
        if user_id in self.active_chats:
            partner_id = self.active_chats[user_id]
            if partner_id in self.active_chats:
                del self.active_chats[partner_id]
            del self.active_chats[user_id]
            
        # Удаляем пользователя
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.users:
            del self.users[user_id]
            
        print(f"❌ Отключен: {user_id}")
        
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except:
                return False
        return False

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Chat Roulette API"}

@app.get("/api/stats")
async def get_stats():
    return {
        "success": True,
        "data": {
            "online_users": len(manager.active_connections),
            "waiting_users": len(manager.waiting_queue),
            "active_chats": len(manager.active_chats) // 2
        }
    }

@app.post("/api/user/create")
async def create_user():
    user_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    name = f"User_{user_id[:4]}"
    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "name": name
        }
    }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"🔌 Попытка подключения WebSocket для {user_id}")
    
    try:
        await manager.connect(user_id, websocket)
        print(f"✅ WebSocket подключен для {user_id}")
        
        while True:
            data = await websocket.receive_text()
            print(f"📨 Получено от {user_id}: {data}")
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                msg_data = message.get("data", {})
                
                if msg_type == "user:join":
                    name = msg_data.get("name", manager.users[user_id]["name"])
                    manager.users[user_id]["name"] = name
                    await manager.send_to_user(user_id, {
                        "type": "user:joined",
                        "data": {"name": name}
                    })
                    
                elif msg_type == "partner:search":
                    print(f"🔍 {user_id} ищет собеседника")
                    
                    # Если уже в чате - игнорируем
                    if user_id in manager.active_chats:
                        continue
                        
                    # Если уже в очереди - игнорируем
                    if user_id in manager.waiting_queue:
                        continue
                    
                    # Есть кто-то в очереди?
                    if manager.waiting_queue:
                        # Берем первого из очереди
                        partner_id = manager.waiting_queue.pop(0)
                        
                        # ВАЖНО: проверяем что это не тот же пользователь
                        if partner_id == user_id:
                            print(f"⚠️ Нашел сам себя, ищем дальше...")
                            # Если очередь не пуста, берем следующего
                            if manager.waiting_queue:
                                partner_id = manager.waiting_queue.pop(0)
                            else:
                                # Если никого нет, добавляем в очередь
                                manager.waiting_queue.append(user_id)
                                await manager.send_to_user(user_id, {
                                    "type": "searching",
                                    "data": {"message": "Ищем собеседника..."}
                                })
                                continue
                        
                        # СОЗДАЕМ ЧАТ
                        manager.active_chats[user_id] = partner_id
                        manager.active_chats[partner_id] = user_id
                        
                        print(f"🔗 Создан чат: {user_id} - {partner_id}")
                        
                        # Уведомляем первого
                        await manager.send_to_user(user_id, {
                            "type": "partner:found",
                            "data": {
                                "partner": {
                                    "id": partner_id,
                                    "name": manager.users[partner_id]["name"]
                                }
                            }
                        })
                        
                        # Уведомляем второго
                        await manager.send_to_user(partner_id, {
                            "type": "partner:found",
                            "data": {
                                "partner": {
                                    "id": user_id,
                                    "name": manager.users[user_id]["name"]
                                }
                            }
                        })
                    else:
                        # Никого нет в очереди - добавляем
                        manager.waiting_queue.append(user_id)
                        await manager.send_to_user(user_id, {
                            "type": "searching",
                            "data": {"message": "Ищем собеседника..."}
                        })
                        
                elif msg_type == "message:send":
                    text = msg_data.get("text", "")
                    if text and user_id in manager.active_chats:
                        partner_id = manager.active_chats[user_id]
                        await manager.send_to_user(partner_id, {
                            "type": "message:receive",
                            "data": {
                                "text": text,
                                "sender": user_id,
                                "sender_name": manager.users[user_id]["name"]
                            }
                        })
                        
                elif msg_type == "partner:disconnect":
                    if user_id in manager.active_chats:
                        partner_id = manager.active_chats[user_id]
                        
                        # Уведомляем партнера
                        await manager.send_to_user(partner_id, {
                            "type": "partner:disconnected",
                            "data": {"message": "Собеседник отключился"}
                        })
                        
                        # Удаляем из чатов
                        del manager.active_chats[user_id]
                        if partner_id in manager.active_chats:
                            del manager.active_chats[partner_id]
                            
                elif msg_type == "search:cancel":
                    if user_id in manager.waiting_queue:
                        manager.waiting_queue.remove(user_id)
                        
            except json.JSONDecodeError:
                print(f"❌ Ошибка JSON от {user_id}")
                
    except WebSocketDisconnect:
        print(f"⚠️ WebSocket отключен для {user_id}")
        manager.disconnect(user_id)
    except Exception as e:
        print(f"🔥 Ошибка для {user_id}: {e}")
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 ЧАТ-РУЛЕТКА БЭКЕНД")
    print("=" * 50)
    print("📡 Сервер: http://localhost:8000")
    print("🔌 WebSocket: ws://localhost:8000/ws/{user_id}")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)