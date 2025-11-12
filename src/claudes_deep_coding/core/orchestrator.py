"""
Code Orchestrator - Main agent that manages and delegates to subagents.
"""

from typing import Any, Dict, List, Optional
import asyncio
from datetime import datetime

from ..agents.base import BaseAgent
from ..agents.researcher import ResearcherAgent
from ..agents.generator import GeneratorAgent
from ..agents.tester import TesterAgent
from ..agents.refiner import RefinerAgent
from ..core.planner import TodoPlanner, Task, TaskPriority, TaskStatus
from ..middleware.subagent import SubAgentMiddleware, MessageType, AgentMessage
from ..persistence.store import FilesystemPersistence


class CodeOrchestrator(BaseAgent):
    """
    Main orchestrator agent that:
    - Manages the overall workflow
    - Delegates tasks to specialized subagents
    - Tracks progress using the todo planner
    - Persists state to filesystem
    - Coordinates agent communication via middleware
    """

    def __init__(
        self,
        persistence_path: str = ".claudes_state",
        enable_persistence: bool = True
    ):
        super().__init__(
            agent_id="orchestrator",
            name="Code Orchestrator",
            description="Main agent that orchestrates code workflow and delegates to subagents"
        )
        
        # Initialize core components
        self.planner = TodoPlanner()
        self.middleware = SubAgentMiddleware()
        self.persistence = FilesystemPersistence(persistence_path) if enable_persistence else None
        
        # Initialize subagents
        self.researcher = ResearcherAgent()
        self.generator = GeneratorAgent()
        self.tester = TesterAgent()
        self.refiner = RefinerAgent()
        
        # Register all subagents with middleware
        self._register_subagents()
        
        # Workflow tracking
        self.workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_workflow: Dict[str, Any] = {}
        
        # Subscribe to messages
        self.middleware.subscribe_to_messages(
            self.agent_id,
            self._handle_agent_message
        )

    def _register_subagents(self):
        """Register all subagents with the middleware."""
        self.middleware.register_agent(self.agent_id, self)
        self.middleware.register_agent(self.researcher.agent_id, self.researcher)
        self.middleware.register_agent(self.generator.agent_id, self.generator)
        self.middleware.register_agent(self.tester.agent_id, self.tester)
        self.middleware.register_agent(self.refiner.agent_id, self.refiner)

    async def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """The orchestrator can handle any high-level coding workflow."""
        return True

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a high-level coding task by orchestrating subagents.
        
        Args:
            task_data: Task details including workflow requirements
            
        Returns:
            Workflow execution results
        """
        task_id = task_data.get("task_id", "unknown")
        await self.on_task_start(task_id, task_data)
        
        try:
            # Create workflow plan
            workflow_plan = await self._create_workflow_plan(task_data)
            
            # Execute workflow
            result = await self._execute_workflow(workflow_plan)
            
            # Save final state
            if self.persistence:
                await self._save_workflow_state()
            
            await self.on_task_complete(task_id, result)
            
            # Determine if workflow was successful
            workflow_success = result.get("overall_status") == "completed"
            
            return {
                "success": workflow_success,
                "task_id": task_id,
                "workflow_id": self.workflow_id,
                "result": result
            }
        
        except Exception as e:
            error_msg = str(e)
            await self.on_task_fail(task_id, error_msg)
            return {
                "success": False,
                "task_id": task_id,
                "workflow_id": self.workflow_id,
                "error": error_msg
            }

    async def _create_workflow_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a workflow plan with tasks for each phase.
        
        Args:
            task_data: High-level task requirements
            
        Returns:
            Workflow plan with organized tasks
        """
        workflow_type = task_data.get("workflow_type", "standard")
        
        # Standard workflow: Research -> Generate -> Test -> Refine
        plan = {
            "workflow_id": self.workflow_id,
            "workflow_type": workflow_type,
            "phases": []
        }
        
        # Phase 1: Research
        research_task = self.planner.create_task(
            title="Research and Discovery",
            description=f"Research requirements for: {task_data.get('description', 'task')}",
            priority=TaskPriority.HIGH,
            metadata={"phase": "research", "agent": "researcher"}
        )
        plan["phases"].append(research_task)
        
        # Phase 2: Generation (depends on research)
        generate_task = self.planner.create_task(
            title="Code Generation",
            description=f"Generate code based on research findings",
            priority=TaskPriority.HIGH,
            dependencies=[research_task.id],
            metadata={"phase": "generation", "agent": "generator"}
        )
        plan["phases"].append(generate_task)
        
        # Phase 3: Testing (depends on generation)
        test_task = self.planner.create_task(
            title="Testing and Validation",
            description="Test and validate generated code",
            priority=TaskPriority.HIGH,
            dependencies=[generate_task.id],
            metadata={"phase": "testing", "agent": "tester"}
        )
        plan["phases"].append(test_task)
        
        # Phase 4: Refinement (depends on testing)
        refine_task = self.planner.create_task(
            title="Code Refinement",
            description="Optimize and refine code for production",
            priority=TaskPriority.MEDIUM,
            dependencies=[test_task.id],
            metadata={"phase": "refinement", "agent": "refiner"}
        )
        plan["phases"].append(refine_task)
        
        if self.persistence:
            await self.persistence.log_workflow_event(
                self.workflow_id,
                "workflow_plan_created",
                {"task_count": len(plan["phases"])}
            )
        
        return plan

    async def _execute_workflow(self, workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow by delegating to appropriate subagents.
        
        Args:
            workflow_plan: Workflow plan with tasks
            
        Returns:
            Workflow execution results
        """
        results = {
            "workflow_id": self.workflow_id,
            "phases_completed": [],
            "overall_status": "in_progress"
        }
        
        # Execute tasks in order based on dependencies
        while True:
            next_task = self.planner.get_next_task()
            
            if not next_task:
                # Check if all tasks are complete
                pending = self.planner.get_pending_tasks()
                if not pending:
                    break
                # If there are pending tasks but none available, we're blocked
                await asyncio.sleep(0.1)
                continue
            
            # Delegate task to appropriate subagent
            agent_id = next_task.metadata.get("agent")
            phase = next_task.metadata.get("phase")
            
            phase_result = await self._delegate_to_subagent(agent_id, next_task)
            
            # Update task status based on result
            if phase_result.get("success"):
                next_task.mark_completed()
                results["phases_completed"].append({
                    "phase": phase,
                    "task_id": next_task.id,
                    "result": phase_result
                })
            else:
                next_task.mark_failed(phase_result.get("error"))
                results["overall_status"] = "failed"
                results["failed_phase"] = phase
                break
        
        # Determine overall status
        if results["overall_status"] != "failed":
            completed = len(self.planner.get_completed_tasks())
            total = len(self.planner.tasks)
            if completed == total:
                results["overall_status"] = "completed"
        
        return results

    async def _delegate_to_subagent(
        self,
        agent_id: str,
        task: Task
    ) -> Dict[str, Any]:
        """
        Delegate a task to a specific subagent.
        
        Args:
            agent_id: ID of the subagent to delegate to
            task: Task to delegate
            
        Returns:
            Task execution result
        """
        # Mark task as in progress
        task.mark_in_progress(agent_id)
        
        # Get the appropriate subagent
        agent_map = {
            "researcher": self.researcher,
            "generator": self.generator,
            "tester": self.tester,
            "refiner": self.refiner
        }
        
        subagent = agent_map.get(agent_id)
        if not subagent:
            return {
                "success": False,
                "error": f"Unknown agent: {agent_id}"
            }
        
        # Prepare task data for subagent
        task_data = {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.metadata.get("phase", "general"),
            "specifications": task.metadata
        }
        
        # Log delegation
        if self.persistence:
            await self.persistence.log_task_action(
                task.id,
                agent_id,
                "delegated",
                {"from": self.agent_id}
            )
        
        # Send task via middleware
        await self.middleware.delegate_task(
            self.agent_id,
            agent_id,
            task_data
        )
        
        # Execute task
        result = await subagent.execute_task(task_data)
        
        # Log completion
        if self.persistence:
            await self.persistence.log_task_action(
                task.id,
                agent_id,
                "completed" if result.get("success") else "failed",
                result
            )
        
        return result

    async def _handle_agent_message(self, message: AgentMessage):
        """
        Handle messages received from subagents.
        
        Args:
            message: Message from a subagent
        """
        if message.message_type == MessageType.STATUS_UPDATE:
            # Update our knowledge of agent status
            agent_status = message.payload.get("status")
            print(f"Agent {message.from_agent} status: {agent_status}")
        
        elif message.message_type == MessageType.TASK_RESULT:
            # Process task results
            print(f"Received result from {message.from_agent}")

    async def _save_workflow_state(self):
        """Save current workflow state to persistence."""
        if not self.persistence:
            return
        
        state = {
            "workflow_id": self.workflow_id,
            "planner_state": {
                "tasks": {
                    task_id: task.model_dump(mode='json')
                    for task_id, task in self.planner.tasks.items()
                },
                "progress": self.planner.get_progress_summary()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await self.persistence.save_agent_state(self.agent_id, state)

    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get current workflow status.
        
        Returns:
            Workflow status and progress
        """
        return {
            "workflow_id": self.workflow_id,
            "orchestrator_status": self.get_status(),
            "planner_progress": self.planner.get_progress_summary(),
            "subagent_status": {
                "researcher": self.researcher.get_status(),
                "generator": self.generator.get_status(),
                "tester": self.tester.get_status(),
                "refiner": self.refiner.get_status()
            }
        }
