from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router
from app.api.websocket import websocket_endpoint

def create_app() -> FastAPI:
    app = FastAPI(
        title="Chat Roulette API",
        description="Бэкенд для чат-рулетки",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключаем роуты
    app.include_router(router, prefix="/api")
    
    # WebSocket endpoint
    app.websocket("/ws/{user_id}")(websocket_endpoint)
    
    return app
