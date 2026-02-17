import os
from typing import List

class Settings:
    PROJECT_NAME: str = "Chat Roulette"
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    ALLOWED_ORIGINS: List[str] = ["*"]
    
settings = Settings()
