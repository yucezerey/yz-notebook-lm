from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time task progress."""

    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self._connections:
            self._connections[task_id] = []
        self._connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        if task_id in self._connections:
            self._connections[task_id] = [
                ws for ws in self._connections[task_id] if ws != websocket
            ]
            if not self._connections[task_id]:
                del self._connections[task_id]

    async def send_progress(self, task_id: str, message: str, progress: int = 0):
        if task_id not in self._connections:
            return
        data = {"type": "progress", "task_id": task_id, "message": message, "progress": progress}
        for ws in self._connections[task_id]:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    async def send_completed(self, task_id: str, result: str | None = None):
        if task_id not in self._connections:
            return
        data = {"type": "completed", "task_id": task_id, "result": result}
        for ws in self._connections[task_id]:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    async def send_error(self, task_id: str, error: str):
        if task_id not in self._connections:
            return
        data = {"type": "error", "task_id": task_id, "error": error}
        for ws in self._connections[task_id]:
            try:
                await ws.send_json(data)
            except Exception:
                pass


ws_manager = ConnectionManager()
