from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_URL
from app.firebase_auth import init_firebase
from app.routers import chat, notebooks, notebooklm_auth
from app.websocket.connection_manager import ws_manager

app = FastAPI(
    title="NotebookLM Dashboard API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_firebase()


app.include_router(notebooklm_auth.router)
app.include_router(notebooks.router)
app.include_router(chat.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await ws_manager.connect(websocket, task_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "cancel_task":
                pass  # TODO: implement task cancellation
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, task_id)
