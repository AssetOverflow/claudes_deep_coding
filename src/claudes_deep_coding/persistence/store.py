"""
Filesystem Persistence - Manages state persistence for agents.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import aiosqlite
import asyncio


class FilesystemPersistence:
    """
    Manages persistence of agent state to the filesystem.
    Supports both file-based and SQLite-based storage.
    """

    def __init__(self, base_path: str = ".claudes_state"):
        """
        Initialize the persistence layer.
        
        Args:
            base_path: Base directory for storing agent state
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.state_dir = self.base_path / "state"
        self.state_dir.mkdir(exist_ok=True)
        self.db_path = self.base_path / "agent_state.db"
        self._initialized = False

    async def initialize(self):
        """Initialize the database schema."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    state_data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            await db.commit()
        
        self._initialized = True

    async def save_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """
        Save agent state to the database.
        
        Args:
            agent_id: Unique identifier for the agent
            state: State dictionary to persist
        """
        await self.initialize()
        
        state_json = json.dumps(state)
        timestamp = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO agent_state (agent_id, state_data, updated_at)
                VALUES (?, ?, ?)
                """,
                (agent_id, state_json, timestamp)
            )
            await db.commit()

    async def load_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load agent state from the database.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            State dictionary or None if not found
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT state_data FROM agent_state WHERE agent_id = ?",
                (agent_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None

    async def log_task_action(
        self,
        task_id: str,
        agent_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a task action to the history.
        
        Args:
            task_id: Task identifier
            agent_id: Agent performing the action
            action: Action being performed
            metadata: Additional metadata about the action
        """
        await self.initialize()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO task_history (task_id, agent_id, action, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, agent_id, action, timestamp, metadata_json)
            )
            await db.commit()

    async def get_task_history(self, task_id: str) -> list:
        """
        Get the history of actions for a specific task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of history entries
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT agent_id, action, timestamp, metadata
                FROM task_history
                WHERE task_id = ?
                ORDER BY timestamp ASC
                """,
                (task_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "agent_id": row[0],
                        "action": row[1],
                        "timestamp": row[2],
                        "metadata": json.loads(row[3]) if row[3] else None
                    }
                    for row in rows
                ]

    async def log_workflow_event(
        self,
        workflow_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ):
        """
        Log a workflow event.
        
        Args:
            workflow_id: Workflow identifier
            event_type: Type of event
            event_data: Event data
        """
        await self.initialize()
        
        timestamp = datetime.now().isoformat()
        event_json = json.dumps(event_data) if event_data else None
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO workflow_logs (workflow_id, event_type, event_data, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (workflow_id, event_type, event_json, timestamp)
            )
            await db.commit()

    async def get_workflow_logs(self, workflow_id: str) -> list:
        """
        Get all logs for a specific workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            List of log entries
        """
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT event_type, event_data, timestamp
                FROM workflow_logs
                WHERE workflow_id = ?
                ORDER BY timestamp ASC
                """,
                (workflow_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "event_type": row[0],
                        "event_data": json.loads(row[1]) if row[1] else None,
                        "timestamp": row[2]
                    }
                    for row in rows
                ]

    def save_state_file(self, filename: str, data: Dict[str, Any]):
        """
        Save state to a JSON file.
        
        Args:
            filename: Name of the file
            data: Data to save
        """
        file_path = self.state_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_state_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load state from a JSON file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Data or None if file doesn't exist
        """
        file_path = self.state_dir / filename
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def clear_all_state(self):
        """Clear all persisted state (use with caution)."""
        if self.db_path.exists():
            os.remove(self.db_path)
        
        for file in self.state_dir.glob("*.json"):
            os.remove(file)
        
        self._initialized = False
