# config.py - конфигурация
import os
from typing import List

class Settings:
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "Chat Roulette API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Сервер
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # WebSocket
    WS_MAX_CONNECTIONS: int = 10000
    WS_PING_INTERVAL: int = 20
    WS_PING_TIMEOUT: int = 20
    
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://yourdomain.com"
    ]
    
    # Ограничения
    MAX_MESSAGE_LENGTH: int = 500
    MAX_USERNAME_LENGTH: int = 30
    RATE_LIMIT_MESSAGES: int = 10  # сообщений в секунду
    RATE_LIMIT_WINDOW: int = 1  # секунд
    
    # Таймауты
    SEARCH_TIMEOUT: int = 60  # секунд ожидания собеседника
    ROOM_TIMEOUT: int = 3600  # секунд жизни комнаты

settings = Settings() жизни комнаты

settings = Settings()