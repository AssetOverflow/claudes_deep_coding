# Claude's Deep Coding

A hierarchical AI agent system built with LangChain's DeepAgents architecture, designed around Claude-Code-style agents and subagents for deep, production-grade coding workflows.

## Overview

**Claude's Deep Coding** implements a sophisticated multi-agent system that orchestrates complex code workflows through specialized subagents. The system features:

- 🎯 **Hierarchical Architecture**: Main orchestrator delegating to specialized subagents
- 📋 **Todo Planner**: Intelligent task planning with dependency tracking
- 💾 **Filesystem Persistence**: State management and workflow history
- 🔄 **SubAgent Middleware**: Seamless communication between agents
- 🤖 **Four Specialized Agents**: Each handling specific aspects of the development workflow

## Architecture

### Core Components

1. **Code Orchestrator** - Main agent that manages the overall workflow
2. **Todo Planner** - Hierarchical task management with dependency tracking
3. **Filesystem Persistence** - SQLite-based state persistence
4. **SubAgent Middleware** - Message routing and delegation system

### Specialized Subagents

#### 🔍 Researcher Agent
Handles discovery and analysis:
- Code exploration and analysis
- API and library research
- Requirements gathering
- Technology stack investigation
- Architecture exploration

#### 🏗️ Generator Agent
Handles code creation:
- Code generation
- Module creation
- Template instantiation
- Boilerplate generation
- Scaffold creation

#### 🧪 Tester Agent
Handles validation and quality:
- Unit testing
- Integration testing
- Code validation
- Quality assurance
- Performance testing

#### ✨ Refiner Agent
Handles optimization:
- Code optimization
- Performance tuning
- Refactoring
- Production hardening
- Documentation enhancement

## Installation

```bash
# Clone the repository
git clone https://github.com/AssetOverflow/claudes_deep_coding.git
cd claudes_deep_coding

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

### Basic Workflow

```python
import asyncio
from claudes_deep_coding import CodeOrchestrator

async def main():
    # Initialize the orchestrator
    orchestrator = CodeOrchestrator(
        persistence_path=".claudes_state",
        enable_persistence=True
    )
    
    # Define a coding task
    task = {
        "task_id": "my_task",
        "workflow_type": "standard",
        "description": "Create a Python module for data validation",
        "requirements": [
            "Input validation functions",
            "Type checking",
            "Error handling",
            "Comprehensive tests"
        ]
    }
    
    # Execute the workflow
    result = await orchestrator.execute_task(task)
    
    # Check results
    if result['success']:
        print(f"Workflow completed successfully!")
        print(f"Workflow ID: {result['workflow_id']}")
    else:
        print(f"Workflow failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Workflow

```python
from claudes_deep_coding.core.orchestrator import CodeOrchestrator
from claudes_deep_coding.core.planner import TaskPriority

async def custom_workflow():
    orchestrator = CodeOrchestrator()
    
    # Create custom tasks with dependencies
    research = orchestrator.planner.create_task(
        title="Research API Design",
        description="Research REST API best practices",
        priority=TaskPriority.HIGH,
        metadata={"phase": "research", "agent": "researcher"}
    )
    
    generate = orchestrator.planner.create_task(
        title="Generate API Code",
        description="Create API endpoints",
        priority=TaskPriority.HIGH,
        dependencies=[research.id],
        metadata={"phase": "generation", "agent": "generator"}
    )
    
    # Execute custom workflow
    workflow_plan = {
        "workflow_id": orchestrator.workflow_id,
        "workflow_type": "custom",
        "phases": [research, generate]
    }
    
    result = await orchestrator._execute_workflow(workflow_plan)
    return result

asyncio.run(custom_workflow())
```

## Workflow Phases

The standard workflow follows a four-phase approach:

1. **Research Phase** (Researcher Agent)
   - Analyzes requirements
   - Discovers relevant APIs and libraries
   - Examines existing code patterns

2. **Generation Phase** (Generator Agent)
   - Creates code based on research findings
   - Generates modules, functions, and classes
   - Produces initial implementation

3. **Testing Phase** (Tester Agent)
   - Validates generated code
   - Runs unit and integration tests
   - Ensures quality standards

4. **Refinement Phase** (Refiner Agent)
   - Optimizes code performance
   - Refactors for maintainability
   - Hardens for production deployment

## Features

### Todo Planner

The planner manages tasks with:
- Priority levels (Critical, High, Medium, Low)
- Dependency tracking
- Status management (Pending, In Progress, Completed, Failed)
- Progress metrics and summaries

```python
# Create a task
task = orchestrator.planner.create_task(
    title="Implement Feature X",
    description="Add new feature with tests",
    priority=TaskPriority.HIGH,
    dependencies=["task_1", "task_2"]
)

# Get next available task
next_task = orchestrator.planner.get_next_task()

# Check progress
progress = orchestrator.planner.get_progress_summary()
print(f"Completion: {progress['completion_percentage']}%")
```

### Persistence Layer

State is automatically persisted to SQLite:
- Agent states
- Task history
- Workflow logs

```python
# Persistence is automatic when enabled
orchestrator = CodeOrchestrator(
    persistence_path=".my_state",
    enable_persistence=True
)

# Manually save state
await orchestrator._save_workflow_state()

# Access persistence directly
await orchestrator.persistence.log_workflow_event(
    workflow_id="my_workflow",
    event_type="custom_event",
    event_data={"key": "value"}
)
```

### SubAgent Middleware

Handles inter-agent communication:
- Message routing
- Task delegation
- Status updates
- Request/response correlation

```python
# Send message between agents
await orchestrator.middleware.send_message(
    from_agent="orchestrator",
    to_agent="researcher",
    message_type=MessageType.TASK_ASSIGNMENT,
    payload={"task": "research_data"}
)

# Broadcast status
await orchestrator.middleware.broadcast_status(
    agent_id="generator",
    status_data={"progress": 50}
)
```

## Examples

Check out the `src/claudes_deep_coding/examples/` directory for:

- `basic_workflow.py` - Standard workflow execution
- `custom_workflow.py` - Custom task creation and execution

Run examples:
```bash
python -m claudes_deep_coding.examples.basic_workflow
python -m claudes_deep_coding.examples.custom_workflow
```

## Project Structure

```
claudes_deep_coding/
├── src/
│   └── claudes_deep_coding/
│       ├── __init__.py
│       ├── core/
│       │   ├── orchestrator.py    # Main orchestrator agent
│       │   └── planner.py         # Todo planner
│       ├── agents/
│       │   ├── base.py            # Base agent class
│       │   ├── researcher.py      # Research agent
│       │   ├── generator.py       # Code generation agent
│       │   ├── tester.py          # Testing agent
│       │   └── refiner.py         # Refinement agent
│       ├── middleware/
│       │   └── subagent.py        # SubAgent middleware
│       ├── persistence/
│       │   └── store.py           # Filesystem persistence
│       └── examples/
│           ├── basic_workflow.py
│           └── custom_workflow.py
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Requirements

- Python 3.9+
- LangChain >= 0.1.0
- LangGraph >= 0.0.20
- Pydantic >= 2.0.0
- aiosqlite >= 0.19.0

### Contributing

Contributions are welcome! This is a foundational implementation that can be extended with:

- Integration with actual LLMs (Claude, GPT-4, etc.)
- Real code execution capabilities
- Advanced planning algorithms
- More specialized agents
- Web interface for workflow monitoring
- Additional persistence backends

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built on concepts from:
- LangChain's agent framework
- LangGraph for agent orchestration
- DeepAgents architecture patterns
- Claude-Code agent design principles
