import uvicorn
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ЧАТ-РУЛЕТКА БЭКЕНД")
    print("=" * 50)
    print("📡 Сервер: http://localhost:8000")
    print("🔌 WebSocket: ws://localhost:8000/ws/{user_id}")
    print("=" * 50)
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
