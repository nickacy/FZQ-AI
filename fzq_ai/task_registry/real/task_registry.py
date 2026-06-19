"""
FZQ-AI Task Registry — Real System
TaskRegistry class. Registers tasks. Tracks status (pending, running, completed, failed).
Stores history. Async-safe. Has register_task(), start_task(), complete_task(), fail_task(),
cancel_task(), get_task(), list_tasks(), list_by_status(), list_by_type(), delete_task(),
clear_all(), reset(), get_stats().
"""
import asyncio
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    PIPELINE_RUN = "pipeline_run"
    REPORT_GENERATION = "report_generation"
    DATA_FETCHING = "data_fetching"
    ANALYSIS = "analysis"
    SCHEDULING = "scheduling"


class TaskPriority(int, Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Task(BaseModel):
    id: str
    type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)


class TaskHistory(BaseModel):
    task_id: str
    events: List[Dict[str, Any]] = Field(default_factory=list)


class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = None
    type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None


class TaskSchedule(BaseModel):
    task_id: str
    cron_expression: Optional[str] = None
    next_run_at: Optional[datetime] = None
    enabled: bool = True


class TaskStats(BaseModel):
    total: int = 0
    pending: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0


class TaskRegistry:
    """Async-safe task registry with status tracking and history."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._history: Dict[str, TaskHistory] = {}
        self._lock = asyncio.Lock()

    async def register_task(
        self,
        task_id: str,
        task_type: TaskType,
        payload: Optional[Dict[str, Any]] = None,
        priority: Optional[TaskPriority] = None,
    ) -> Task:
        """Register a new task."""
        async with self._lock:
            task = Task(
                id=task_id,
                type=task_type,
                payload=payload or {},
                priority=priority or TaskPriority.NORMAL,
            )
            self._tasks[task_id] = task
            self._history[task_id] = TaskHistory(
                task_id=task_id,
                events=[
                    {
                        "event": "registered",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ],
            )
            return task

    async def start_task(self, task_id: str) -> Task:
        """Mark a task as running."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self._history[task_id].events.append(
                {
                    "event": "started",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return task

    async def complete_task(self, task_id: str, result: Optional[Any] = None) -> Task:
        """Mark a task as completed."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            self._history[task_id].events.append(
                {
                    "event": "completed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result,
                }
            )
            return task

    async def fail_task(self, task_id: str, error: Optional[str] = None) -> Task:
        """Mark a task as failed."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = error
            self._history[task_id].events.append(
                {
                    "event": "failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": error,
                }
            )
            return task

    async def cancel_task(self, task_id: str) -> Task:
        """Mark a task as cancelled."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            self._history[task_id].events.append(
                {
                    "event": "cancelled",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def list_tasks(self) -> List[Task]:
        """List all tasks."""
        async with self._lock:
            return list(self._tasks.values())

    async def list_by_status(self, status: TaskStatus) -> List[Task]:
        """List tasks filtered by status."""
        async with self._lock:
            return [t for t in self._tasks.values() if t.status == status]

    async def list_by_type(self, task_type: TaskType) -> List[Task]:
        """List tasks filtered by type."""
        async with self._lock:
            return [t for t in self._tasks.values() if t.type == task_type]

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    async def clear_all(self) -> None:
        """Clear all tasks and history."""
        async with self._lock:
            self._tasks.clear()
            self._history.clear()

    async def reset(self) -> None:
        """Reset the registry (clear all tasks and history)."""
        async with self._lock:
            self._tasks.clear()
            self._history.clear()

    async def get_stats(self) -> TaskStats:
        """Return statistics about tasks."""
        async with self._lock:
            stats = TaskStats()
            stats.total = len(self._tasks)
            stats.pending = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.PENDING
            )
            stats.running = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING
            )
            stats.completed = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED
            )
            stats.failed = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.FAILED
            )
            stats.cancelled = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.CANCELLED
            )
            return stats
