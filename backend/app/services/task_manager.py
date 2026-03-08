import uuid
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskManager:
    """In-memory task tracker for long-running operations."""

    def __init__(self):
        self._tasks: dict[str, dict[str, Any]] = {}

    def create(self, task_type: str, params: dict | None = None) -> str:
        task_id = str(uuid.uuid4())[:8]
        self._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": TaskStatus.QUEUED,
            "params": params or {},
            "result": None,
            "error": None,
            "progress_messages": [],
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
        }
        return task_id

    def get(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    def set_running(self, task_id: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = TaskStatus.RUNNING

    def set_completed(self, task_id: str, result: Any = None):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = TaskStatus.COMPLETED
            self._tasks[task_id]["result"] = result
            self._tasks[task_id]["completed_at"] = datetime.now().isoformat()

    def set_failed(self, task_id: str, error: str):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = TaskStatus.FAILED
            self._tasks[task_id]["error"] = error
            self._tasks[task_id]["completed_at"] = datetime.now().isoformat()

    def add_progress(self, task_id: str, message: str):
        if task_id in self._tasks:
            self._tasks[task_id]["progress_messages"].append(message)

    def list_tasks(self, task_type: str | None = None) -> list[dict]:
        tasks = list(self._tasks.values())
        if task_type:
            tasks = [t for t in tasks if t["type"] == task_type]
        return sorted(tasks, key=lambda t: t["created_at"], reverse=True)


task_manager = TaskManager()
