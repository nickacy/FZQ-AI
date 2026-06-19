"""
FZQ-AI Task Registry — Test Adapter
MockTaskRegistry. Same interface as real TaskRegistry. In-memory dict.
Pre-seeded with 3 mock tasks (pipeline_run COMPLETED, report_generation RUNNING, data_fetching PENDING).
Returns fixed mock data. No real DB. No real scheduling. reset() re-injects mocks.
"""
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


class MockTaskRegistry:
    """In-memory mock task registry. Pre-seeded with 3 mock tasks."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._history: Dict[str, TaskHistory] = {}
        self._seed_mocks()

    def _seed_mocks(self) -> None:
        """Inject the 3 pre-seeded mock tasks."""
        tasks = [
            Task(
                id="mock-task-1",
                type=TaskType.PIPELINE_RUN,
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.NORMAL,
            ),
            Task(
                id="mock-task-2",
                type=TaskType.REPORT_GENERATION,
                status=TaskStatus.RUNNING,
                priority=TaskPriority.HIGH,
            ),
            Task(
                id="mock-task-3",
                type=TaskType.DATA_FETCHING,
                status=TaskStatus.PENDING,
                priority=TaskPriority.LOW,
            ),
        ]
        for t in tasks:
            self._tasks[t.id] = t
            self._history[t.id] = TaskHistory(
                task_id=t.id,
                events=[
                    {
                        "event": "registered",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ],
            )

    def register_task(
        self,
        task_id: str,
        task_type: TaskType,
        payload: Optional[Dict[str, Any]] = None,
        priority: Optional[TaskPriority] = None,
    ) -> Task:
        """Register a new task."""
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

    def start_task(self, task_id: str) -> Task:
        """Mark a task as running."""
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

    def complete_task(self, task_id: str, result: Optional[Any] = None) -> Task:
        """Mark a task as completed."""
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

    def fail_task(self, task_id: str, error: Optional[str] = None) -> Task:
        """Mark a task as failed."""
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

    def cancel_task(self, task_id: str) -> Task:
        """Mark a task as cancelled."""
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

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        """List all tasks."""
        return list(self._tasks.values())

    def list_by_status(self, status: TaskStatus) -> List[Task]:
        """List tasks filtered by status."""
        return [t for t in self._tasks.values() if t.status == status]

    def list_by_type(self, task_type: TaskType) -> List[Task]:
        """List tasks filtered by type."""
        return [t for t in self._tasks.values() if t.type == task_type]

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear_all(self) -> None:
        """Clear all tasks and history."""
        self._tasks.clear()
        self._history.clear()

    def reset(self) -> None:
        """Reset the registry and re-inject mock tasks."""
        self._tasks.clear()
        self._history.clear()
        self._seed_mocks()

    def get_stats(self) -> TaskStats:
        """Return statistics about tasks."""
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
