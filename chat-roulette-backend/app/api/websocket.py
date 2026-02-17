from fastapi import WebSocket, WebSocketDisconnect
import json
from app.core.manager import manager

async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"Попытка подключения WebSocket для {user_id}")
    
    try:
        await manager.connect(user_id, websocket)
        print(f"WebSocket подключен для {user_id}")
        
        while True:
            data = await websocket.receive_text()
            print(f"Получено от {user_id}: {data}")
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                msg_data = message.get("data", {})
                
                if msg_type == "user:join":
                    name = msg_data.get("name", manager.users[user_id].name)
                    manager.users[user_id].name = name
                    await manager.send_to_user(user_id, {
                        "type": "user:joined",
                        "data": {"name": name}
                    })
                    
                elif msg_type == "partner:search":
                    print(f"{user_id} ищет собеседника")
                    
                    if user_id in manager.active_chats:
                        continue
                        
                    if user_id in manager.waiting_queue:
                        continue
                    
                    if manager.waiting_queue:
                        partner_id = manager.waiting_queue.pop(0)
                        
                        if partner_id == user_id:
                            print(f"Нашел сам себя, ищем дальше...")
                            if manager.waiting_queue:
                                partner_id = manager.waiting_queue.pop(0)
                            else:
                                manager.waiting_queue.append(user_id)
                                await manager.send_to_user(user_id, {
                                    "type": "searching",
                                    "data": {"message": "Ищем собеседника..."}
                                })
                                continue
                        
                        manager.active_chats[user_id] = partner_id
                        manager.active_chats[partner_id] = user_id
                        
                        print(f"Создан чат: {user_id} - {partner_id}")
                        
                        await manager.send_to_user(user_id, {
                            "type": "partner:found",
                            "data": {
                                "partner": {
                                    "id": partner_id,
                                    "name": manager.users[partner_id].name
                                }
                            }
                        })
                        
                        await manager.send_to_user(partner_id, {
                            "type": "partner:found",
                            "data": {
                                "partner": {
                                    "id": user_id,
                                    "name": manager.users[user_id].name
                                }
                            }
                        })
                    else:
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
                                "sender_name": manager.users[user_id].name
                            }
                        })
                        
                elif msg_type == "partner:disconnect":
                    if user_id in manager.active_chats:
                        partner_id = manager.active_chats[user_id]
                        
                        await manager.send_to_user(partner_id, {
                            "type": "partner:disconnected",
                            "data": {"message": "Собеседник отключился"}
                        })
                        
                        del manager.active_chats[user_id]
                        if partner_id in manager.active_chats:
                            del manager.active_chats[partner_id]
                            
                elif msg_type == "search:cancel":
                    if user_id in manager.waiting_queue:
                        manager.waiting_queue.remove(user_id)
                        
            except json.JSONDecodeError:
                print(f"Ошибка JSON от {user_id}")
                
    except WebSocketDisconnect:
        print(f"WebSocket отключен для {user_id}")
        manager.disconnect(user_id)
    except Exception as e:
        print(f"Ошибка для {user_id}: {e}")
        manager.disconnect(user_id)