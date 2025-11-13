"""
Tests for the DeepAgents hierarchical AI system.
"""

import pytest
import asyncio
from claudes_deep_coding import CodeOrchestrator
from claudes_deep_coding.core.planner import TodoPlanner, TaskPriority, TaskStatus
from claudes_deep_coding.agents import ResearcherAgent, GeneratorAgent, TesterAgent, RefinerAgent


class TestTodoPlanner:
    """Test the TodoPlanner functionality."""
    
    def test_create_task(self):
        """Test creating a task."""
        planner = TodoPlanner()
        task = planner.create_task(
            title="Test Task",
            description="A test task",
            priority=TaskPriority.HIGH
        )
        
        assert task.id == "task_1"
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
    
    def test_task_dependencies(self):
        """Test task dependency tracking."""
        planner = TodoPlanner()
        task1 = planner.create_task(
            title="Task 1",
            description="First task"
        )
        task2 = planner.create_task(
            title="Task 2",
            description="Second task",
            dependencies=[task1.id]
        )
        
        # Task 2 should not be available until Task 1 is complete
        next_task = planner.get_next_task()
        assert next_task.id == task1.id
        
        # Complete task 1
        task1.mark_completed()
        
        # Now task 2 should be available
        next_task = planner.get_next_task()
        assert next_task.id == task2.id
    
    def test_progress_summary(self):
        """Test progress summary calculation."""
        planner = TodoPlanner()
        task1 = planner.create_task(title="Task 1", description="First")
        task2 = planner.create_task(title="Task 2", description="Second")
        
        task1.mark_completed()
        
        progress = planner.get_progress_summary()
        assert progress["total_tasks"] == 2
        assert progress["completed"] == 1
        assert progress["pending"] == 1
        assert progress["completion_percentage"] == 50.0


class TestAgents:
    """Test individual agent functionality."""
    
    @pytest.mark.asyncio
    async def test_researcher_agent(self):
        """Test ResearcherAgent can handle research tasks."""
        agent = ResearcherAgent()
        
        task_data = {
            "task_id": "research_1",
            "type": "research",
            "description": "Research API patterns",
            "research_type": "api_discovery",
            "target": "REST API"
        }
        
        can_handle = await agent.can_handle_task(task_data)
        assert can_handle is True
        
        result = await agent.execute_task(task_data)
        assert result["success"] is True
        assert "findings" in result
    
    @pytest.mark.asyncio
    async def test_generator_agent(self):
        """Test GeneratorAgent can handle generation tasks."""
        agent = GeneratorAgent()
        
        task_data = {
            "task_id": "gen_1",
            "type": "generate",
            "description": "Generate module",
            "generation_type": "module",
            "target": "validator"
        }
        
        can_handle = await agent.can_handle_task(task_data)
        assert can_handle is True
        
        result = await agent.execute_task(task_data)
        assert result["success"] is True
        assert "generated_artifacts" in result
    
    @pytest.mark.asyncio
    async def test_tester_agent(self):
        """Test TesterAgent can handle testing tasks."""
        agent = TesterAgent()
        
        task_data = {
            "task_id": "test_1",
            "type": "test",
            "description": "Run unit tests",
            "test_type": "unit",
            "target": "validator"
        }
        
        can_handle = await agent.can_handle_task(task_data)
        assert can_handle is True
        
        result = await agent.execute_task(task_data)
        assert result["success"] is True
        assert "test_results" in result
    
    @pytest.mark.asyncio
    async def test_refiner_agent(self):
        """Test RefinerAgent can handle refinement tasks."""
        agent = RefinerAgent()
        
        task_data = {
            "task_id": "refine_1",
            "type": "optimize",
            "description": "Optimize code",
            "refinement_type": "optimization",
            "target": "validator"
        }
        
        can_handle = await agent.can_handle_task(task_data)
        assert can_handle is True
        
        result = await agent.execute_task(task_data)
        assert result["success"] is True
        assert "refinements" in result


class TestCodeOrchestrator:
    """Test the CodeOrchestrator functionality."""
    
    @pytest.mark.asyncio
    async def test_basic_workflow(self):
        """Test executing a basic workflow."""
        orchestrator = CodeOrchestrator(
            persistence_path="/tmp/test_orchestrator",
            enable_persistence=False
        )
        
        task = {
            "task_id": "workflow_test",
            "workflow_type": "standard",
            "description": "Test workflow execution"
        }
        
        result = await orchestrator.execute_task(task)
        
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["overall_status"] == "completed"
        assert len(result["result"]["phases_completed"]) == 4
    
    @pytest.mark.asyncio
    async def test_workflow_with_persistence(self):
        """Test workflow execution with persistence enabled."""
        orchestrator = CodeOrchestrator(
            persistence_path="/tmp/test_orchestrator_persist",
            enable_persistence=True
        )
        
        task = {
            "task_id": "workflow_persist_test",
            "workflow_type": "standard",
            "description": "Test workflow with persistence"
        }
        
        result = await orchestrator.execute_task(task)
        
        assert result["success"] is True
        assert result["result"]["overall_status"] == "completed"
    
    def test_workflow_status(self):
        """Test getting workflow status."""
        orchestrator = CodeOrchestrator(enable_persistence=False)
        
        status = orchestrator.get_workflow_status()
        
        assert "workflow_id" in status
        assert "orchestrator_status" in status
        assert "planner_progress" in status
        assert "subagent_status" in status
        
        # Check all subagents are present
        assert "researcher" in status["subagent_status"]
        assert "generator" in status["subagent_status"]
        assert "tester" in status["subagent_status"]
        assert "refiner" in status["subagent_status"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
