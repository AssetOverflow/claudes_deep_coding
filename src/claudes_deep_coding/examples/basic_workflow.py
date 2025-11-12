"""
Example: Basic workflow using the Code Orchestrator.

This example demonstrates how to use the DeepAgents system to execute
a complete code workflow from research to refinement.
"""

import asyncio
from claudes_deep_coding import CodeOrchestrator


async def main():
    """Run a basic code workflow."""
    
    # Initialize the orchestrator
    print("Initializing Code Orchestrator...")
    orchestrator = CodeOrchestrator(
        persistence_path=".example_state",
        enable_persistence=True
    )
    
    # Define a coding task
    task = {
        "task_id": "example_001",
        "workflow_type": "standard",
        "description": "Create a Python module for data validation with tests",
        "requirements": [
            "Input validation functions",
            "Type checking",
            "Error handling",
            "Comprehensive tests"
        ]
    }
    
    print(f"\nStarting workflow: {task['description']}")
    print("=" * 60)
    
    # Execute the workflow
    result = await orchestrator.execute_task(task)
    
    # Display results
    print("\nWorkflow Results:")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Workflow ID: {result['workflow_id']}")
    
    if result['success']:
        workflow_result = result['result']
        print(f"Overall Status: {workflow_result['overall_status']}")
        print(f"\nPhases Completed: {len(workflow_result['phases_completed'])}")
        
        for phase_info in workflow_result['phases_completed']:
            phase = phase_info['phase']
            phase_result = phase_info['result']
            print(f"\n  Phase: {phase.upper()}")
            print(f"  Task ID: {phase_info['task_id']}")
            print(f"  Success: {phase_result.get('success', False)}")
            
            # Display phase-specific results
            if phase == 'research':
                findings = phase_result.get('findings', {})
                print(f"  Findings: {findings.get('research_type', 'N/A')}")
            elif phase == 'generation':
                artifacts = phase_result.get('generated_artifacts', {})
                print(f"  Artifacts: {artifacts.get('generation_type', 'N/A')}")
            elif phase == 'testing':
                test_results = phase_result.get('test_results', {})
                print(f"  Tests: {test_results.get('test_type', 'N/A')}")
            elif phase == 'refinement':
                refinements = phase_result.get('refinements', {})
                print(f"  Refinements: {refinements.get('refinement_type', 'N/A')}")
    
    # Get workflow status
    print("\n\nWorkflow Status:")
    print("=" * 60)
    status = orchestrator.get_workflow_status()
    
    progress = status['planner_progress']
    print(f"Total Tasks: {progress['total_tasks']}")
    print(f"Completed: {progress['completed']}")
    print(f"In Progress: {progress['in_progress']}")
    print(f"Pending: {progress['pending']}")
    print(f"Failed: {progress['failed']}")
    print(f"Completion: {progress['completion_percentage']:.1f}%")
    
    print("\n\nSubagent Status:")
    print("=" * 60)
    for agent_name, agent_status in status['subagent_status'].items():
        print(f"\n{agent_name.capitalize()}:")
        print(f"  Status: {agent_status['status']}")
        print(f"  Completed Tasks: {agent_status['completed_tasks']}")
        print(f"  Failed Tasks: {agent_status['failed_tasks']}")


if __name__ == "__main__":
    asyncio.run(main())
