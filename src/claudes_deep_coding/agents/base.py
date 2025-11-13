"""
Base Agent - Abstract base class for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Defines the common interface and functionality.
    """

    def __init__(self, agent_id: str, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            description: Description of agent's capabilities
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.state: Dict[str, Any] = {
            "status": "idle",
            "current_task": None,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "created_at": datetime.now().isoformat(),
        }

    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task_data: Task details and parameters
            
        Returns:
            Result dictionary containing execution results
        """
        pass

    @abstractmethod
    async def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle a specific task.
        
        Args:
            task_data: Task details
            
        Returns:
            True if agent can handle the task
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return self.state.copy()

    def update_status(self, status: str):
        """Update agent status."""
        self.state["status"] = status
        self.state["last_updated"] = datetime.now().isoformat()

    async def on_task_start(self, task_id: str, task_data: Dict[str, Any]):
        """Hook called when a task starts."""
        self.state["current_task"] = task_id
        self.update_status("busy")

    async def on_task_complete(self, task_id: str, result: Dict[str, Any]):
        """Hook called when a task completes successfully."""
        self.state["current_task"] = None
        self.state["completed_tasks"] += 1
        self.update_status("idle")

    async def on_task_fail(self, task_id: str, error: str):
        """Hook called when a task fails."""
        self.state["current_task"] = None
        self.state["failed_tasks"] += 1
        self.update_status("idle")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities description."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.state["status"],
        }
