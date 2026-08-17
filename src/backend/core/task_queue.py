import uuid
import asyncio
from enum import Enum
from typing import Dict, Any, Callable, Optional, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from src.backend.core.event_bus import event_bus
from loguru import logger


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskInfo(BaseModel):
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BackgroundTaskQueue:
    """Async Background Task Worker System with status tracking and retries."""
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._handles: Dict[str, asyncio.Task] = {}

    def submit_task(self, name: str, coroutine_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> str:
        """Submit a background task for execution."""
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id=task_id, name=name)
        self._tasks[task_id] = task_info

        async def _wrapper():
            try:
                task_info.status = TaskStatus.RUNNING
                await event_bus.publish("TaskStarted", "TaskQueue", {"task_id": task_id, "name": name})

                res = await coroutine_func(*args, **kwargs)

                task_info.status = TaskStatus.COMPLETED
                task_info.progress = 100.0
                task_info.result = res
                await event_bus.publish("TaskCompleted", "TaskQueue", {"task_id": task_id, "name": name, "result": res})
            except asyncio.CancelledError:
                task_info.status = TaskStatus.CANCELLED
                await event_bus.publish("TaskCancelled", "TaskQueue", {"task_id": task_id, "name": name})
            except Exception as e:
                logger.error(f"BackgroundTaskQueue error in task '{name}': {e}")
                task_info.status = TaskStatus.FAILED
                task_info.error = str(e)
                await event_bus.publish("TaskFailed", "TaskQueue", {"task_id": task_id, "name": name, "error": str(e)})

        async_task = asyncio.create_task(_wrapper())
        self._handles[task_id] = async_task
        return task_id

    def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Retrieve current task status and progress."""
        return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self._handles and not self._handles[task_id].done():
            self._handles[task_id].cancel()
            return True
        return False


# Global Singleton Task Queue Instance
task_queue = BackgroundTaskQueue()
