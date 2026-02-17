from fastapi import APIRouter
import random
import string
from app.core.manager import manager
from app.models.schemas import UserResponse, StatsResponse

router = APIRouter()

@router.get("/")
async def root():
    return {"status": "ok", "message": "Chat Roulette API"}

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    return {
        "success": True,
        "data": {
            "online_users": manager.get_online_count(),
            "waiting_users": manager.get_waiting_count(),
            "active_chats": manager.get_active_chats_count()
        }
    }

@router.post("/user/create", response_model=UserResponse)
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
