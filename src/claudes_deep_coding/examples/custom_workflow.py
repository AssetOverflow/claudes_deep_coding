"""
Example: Custom workflow with specific task assignments.

This example shows how to create a custom workflow with specific
tasks assigned to different subagents.
"""

import asyncio
from claudes_deep_coding.core.orchestrator import CodeOrchestrator
from claudes_deep_coding.core.planner import TaskPriority


async def main():
    """Run a custom workflow with manual task creation."""
    
    print("Initializing Code Orchestrator for custom workflow...")
    orchestrator = CodeOrchestrator(
        persistence_path=".custom_workflow_state",
        enable_persistence=True
    )
    
    # Create custom tasks directly using the planner
    print("\nCreating custom task plan...")
    
    # Task 1: Research API requirements
    research_task = orchestrator.planner.create_task(
        title="Research REST API Best Practices",
        description="Research modern REST API design patterns and authentication methods",
        priority=TaskPriority.CRITICAL,
        metadata={
            "phase": "research",
            "agent": "researcher",
            "research_type": "api_discovery"
        }
    )
    
    # Task 2: Generate API skeleton
    generate_task = orchestrator.planner.create_task(
        title="Generate API Skeleton",
        description="Create REST API endpoints with proper structure",
        priority=TaskPriority.HIGH,
        dependencies=[research_task.id],
        metadata={
            "phase": "generation",
            "agent": "generator",
            "generation_type": "module",
            "specifications": {
                "endpoints": ["GET /users", "POST /users", "PUT /users/:id"],
                "authentication": "JWT"
            }
        }
    )
    
    # Task 3: Generate API tests
    test_generation_task = orchestrator.planner.create_task(
        title="Generate API Tests",
        description="Create comprehensive test suite for API",
        priority=TaskPriority.HIGH,
        dependencies=[generate_task.id],
        metadata={
            "phase": "generation",
            "agent": "generator",
            "generation_type": "test"
        }
    )
    
    # Task 4: Run tests
    test_task = orchestrator.planner.create_task(
        title="Execute API Tests",
        description="Run all API tests and validate functionality",
        priority=TaskPriority.HIGH,
        dependencies=[test_generation_task.id],
        metadata={
            "phase": "testing",
            "agent": "tester",
            "test_type": "integration"
        }
    )
    
    # Task 5: Optimize for production
    refine_task = orchestrator.planner.create_task(
        title="Production Hardening",
        description="Optimize API for production deployment",
        priority=TaskPriority.MEDIUM,
        dependencies=[test_task.id],
        metadata={
            "phase": "refinement",
            "agent": "refiner",
            "refinement_type": "production_hardening"
        }
    )
    
    print(f"Created {len(orchestrator.planner.tasks)} tasks")
    
    # Execute workflow
    print("\nExecuting custom workflow...")
    print("=" * 60)
    
    workflow_plan = {
        "workflow_id": orchestrator.workflow_id,
        "workflow_type": "custom",
        "phases": list(orchestrator.planner.tasks.values())
    }
    
    result = await orchestrator._execute_workflow(workflow_plan)
    
    # Display detailed results
    print("\n\nCustom Workflow Results:")
    print("=" * 60)
    print(f"Overall Status: {result['overall_status']}")
    print(f"Phases Completed: {len(result['phases_completed'])}/{len(orchestrator.planner.tasks)}")
    
    for idx, phase_info in enumerate(result['phases_completed'], 1):
        print(f"\n{idx}. Phase: {phase_info['phase'].upper()}")
        phase_result = phase_info['result']
        
        # Show key information from each phase
        if 'findings' in phase_result:
            print(f"   Research Type: {phase_result['findings'].get('research_type', 'N/A')}")
        elif 'generated_artifacts' in phase_result:
            artifacts = phase_result['generated_artifacts']
            print(f"   Generated: {artifacts.get('generation_type', 'N/A')}")
            if 'files_created' in artifacts:
                print(f"   Files: {', '.join(artifacts['files_created'])}")
        elif 'test_results' in phase_result:
            tests = phase_result['test_results']
            print(f"   Tests Passed: {tests.get('tests_passed', 0)}")
            print(f"   Tests Failed: {tests.get('tests_failed', 0)}")
        elif 'refinements' in phase_result:
            refinements = phase_result['refinements']
            improvements = refinements.get('hardening_applied', [])
            print(f"   Improvements: {len(improvements)}")
    
    # Show progress summary
    print("\n\nProgress Summary:")
    print("=" * 60)
    progress = orchestrator.planner.get_progress_summary()
    print(f"Completion Rate: {progress['completion_percentage']:.1f}%")
    print(f"Tasks Completed: {progress['completed']}")
    print(f"Tasks Failed: {progress['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
