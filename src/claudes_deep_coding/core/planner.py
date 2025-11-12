"""
Todo Planner - Manages task planning and tracking for the Code Orchestrator.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task in the todo list."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Priority level of a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Represents a single task in the todo list."""
    id: str = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str = Field(description="Detailed task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    assigned_agent: Optional[str] = Field(default=None, description="Agent assigned to this task")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs this task depends on")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_in_progress(self, agent: str):
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.assigned_agent = agent
        self.updated_at = datetime.now()

    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_failed(self, reason: Optional[str] = None):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()
        if reason:
            self.metadata["failure_reason"] = reason


class TodoPlanner:
    """
    Manages task planning, tracking, and dependencies for the agent system.
    Implements a hierarchical task management system with dependency tracking.
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._task_counter = 0

    def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task and add it to the planner."""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )
        
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its ID."""
        return self.tasks.get(task_id)

    def get_next_task(self) -> Optional[Task]:
        """
        Get the next available task based on dependencies and priority.
        Returns the highest priority task that has no pending dependencies.
        """
        available_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.PENDING
            and self._dependencies_met(task)
        ]
        
        if not available_tasks:
            return None
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }
        
        return sorted(
            available_tasks,
            key=lambda t: (priority_order[t.priority], t.created_at)
        )[0]

    def _dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies for a task are completed."""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]

    def get_in_progress_tasks(self) -> List[Task]:
        """Get all in-progress tasks."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]

    def get_tasks_by_agent(self, agent: str) -> List[Task]:
        """Get all tasks assigned to a specific agent."""
        return [t for t in self.tasks.values() if t.assigned_agent == agent]

    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update the status of a task."""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of overall progress."""
        total = len(self.tasks)
        completed = len(self.get_completed_tasks())
        in_progress = len(self.get_in_progress_tasks())
        pending = len(self.get_pending_tasks())
        failed = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        
        return {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "failed": failed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
        }

    def decompose_task(self, task_id: str, subtasks: List[Dict[str, Any]]) -> List[Task]:
        """
        Decompose a task into smaller subtasks.
        Each subtask will depend on the original task being in progress.
        """
        parent_task = self.tasks.get(task_id)
        if not parent_task:
            raise ValueError(f"Task {task_id} not found")
        
        created_subtasks = []
        for subtask_info in subtasks:
            subtask = self.create_task(
                title=subtask_info.get("title", ""),
                description=subtask_info.get("description", ""),
                priority=subtask_info.get("priority", parent_task.priority),
                dependencies=subtask_info.get("dependencies", []),
                metadata={"parent_task": task_id},
            )
            created_subtasks.append(subtask)
        
        return created_subtasks
