# Architecture

This document describes the architecture of Claude's Deep Coding hierarchical AI agent system.

## System Overview

Claude's Deep Coding implements a hierarchical multi-agent system based on LangChain's DeepAgents architecture. The system orchestrates complex code workflows through specialized subagents, each focusing on specific aspects of the development lifecycle.

```
┌─────────────────────────────────────────────────────┐
│           Code Orchestrator (Main Agent)            │
│  • Workflow planning and execution                  │
│  • Task delegation and coordination                 │
│  • State management and persistence                 │
└──────────────────┬──────────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │  SubAgent Middleware   │
       │  • Message routing     │
       │  • Task delegation     │
       │  • Status tracking     │
       └───────────┬───────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    │              │              │              │
┌───▼────┐   ┌────▼─────┐   ┌───▼────┐   ┌────▼─────┐
│Research│   │Generator │   │ Tester │   │ Refiner  │
│ Agent  │   │  Agent   │   │ Agent  │   │  Agent   │
└────────┘   └──────────┘   └────────┘   └──────────┘
```

## Core Components

### 1. Code Orchestrator

The Code Orchestrator is the main agent responsible for:

- **Workflow Planning**: Creating execution plans using the TodoPlanner
- **Task Delegation**: Assigning tasks to appropriate subagents
- **Progress Tracking**: Monitoring overall workflow progress
- **State Persistence**: Saving and loading workflow state

**Key Methods:**
- `execute_task()`: Executes a high-level coding task
- `_create_workflow_plan()`: Creates a structured workflow plan
- `_execute_workflow()`: Executes the workflow by delegating to subagents
- `_delegate_to_subagent()`: Delegates individual tasks to specific agents

### 2. Todo Planner

The TodoPlanner manages hierarchical task planning with:

- **Dependency Tracking**: Tasks can depend on completion of other tasks
- **Priority Management**: Critical, High, Medium, Low priorities
- **Status Tracking**: Pending, In Progress, Completed, Failed, Blocked
- **Progress Metrics**: Real-time calculation of workflow completion

**Key Features:**
- Automatic dependency resolution
- Task decomposition support
- Progress summaries and metrics
- Agent assignment tracking

### 3. Filesystem Persistence

The persistence layer provides:

- **SQLite Storage**: Efficient structured data storage
- **Agent State**: Persisting individual agent states
- **Task History**: Complete audit trail of task actions
- **Workflow Logs**: Event logging for workflow execution

**Database Schema:**
```sql
-- Agent state storage
agent_state (agent_id, state_data, updated_at)

-- Task execution history
task_history (id, task_id, agent_id, action, timestamp, metadata)

-- Workflow event logs
workflow_logs (id, workflow_id, event_type, event_data, timestamp)
```

### 4. SubAgent Middleware

The middleware layer handles:

- **Message Routing**: Directing messages between agents
- **Task Delegation**: Orchestrating task assignment
- **Request/Response**: Correlation of requests and responses
- **Status Broadcasting**: Distributing status updates

**Message Types:**
- `TASK_ASSIGNMENT`: Delegate a task to an agent
- `TASK_RESULT`: Report task completion results
- `STATUS_UPDATE`: Broadcast status changes
- `REQUEST_HELP`: Request assistance from another agent
- `DELEGATION`: Delegate sub-tasks
- `CANCELLATION`: Cancel pending tasks

## Specialized Subagents

### Researcher Agent

**Capabilities:**
- Code analysis and exploration
- API and library research
- Requirements gathering
- Dependency analysis
- Architecture exploration

**Research Types:**
- `code_analysis`: Analyzes code structure and patterns
- `api_discovery`: Discovers and evaluates APIs
- `dependency_analysis`: Examines project dependencies
- `general`: General-purpose research

### Generator Agent

**Capabilities:**
- Code generation
- Module creation
- Template instantiation
- Boilerplate generation
- Scaffold creation

**Generation Types:**
- `module`: Creates complete modules
- `function`: Generates functions
- `class`: Creates class structures
- `test`: Generates test suites
- `general`: General-purpose code generation

### Tester Agent

**Capabilities:**
- Unit testing
- Integration testing
- Code validation
- Quality assurance
- Performance testing

**Test Types:**
- `unit`: Unit test execution
- `integration`: Integration test execution
- `validation`: Input/output validation
- `performance`: Performance benchmarking

### Refiner Agent

**Capabilities:**
- Code optimization
- Performance tuning
- Refactoring
- Production hardening
- Documentation enhancement

**Refinement Types:**
- `optimization`: Performance optimization
- `refactoring`: Code quality improvements
- `production_hardening`: Production readiness
- `documentation`: Documentation improvements

## Workflow Execution

### Standard Workflow

The standard workflow follows four phases:

```
1. Research Phase (Researcher Agent)
   ↓
2. Generation Phase (Generator Agent)
   ↓
3. Testing Phase (Tester Agent)
   ↓
4. Refinement Phase (Refiner Agent)
```

Each phase depends on the completion of the previous phase, ensuring a structured and predictable workflow.

### Custom Workflows

Custom workflows allow for:
- Non-linear task dependencies
- Multiple instances of the same agent type
- Parallel task execution
- Conditional task execution

Example:
```python
research = planner.create_task(...)
gen1 = planner.create_task(dependencies=[research.id])
gen2 = planner.create_task(dependencies=[research.id])  # Parallel with gen1
test = planner.create_task(dependencies=[gen1.id, gen2.id])
```

## Data Flow

### Task Execution Flow

```
1. Orchestrator creates workflow plan
2. Planner identifies next available task
3. Orchestrator delegates task to appropriate agent
4. Middleware routes task message to agent
5. Agent executes task
6. Agent returns result via middleware
7. Orchestrator updates task status
8. Persistence layer logs action
9. Repeat until all tasks complete
```

### State Management

```
Agent State → Pydantic Model → JSON → SQLite
     ↑                                    ↓
     └────────────────────────────────────┘
```

All state transitions are:
- Validated by Pydantic models
- Serialized to JSON
- Persisted to SQLite
- Restorable on system restart

## Extensibility

The system is designed for extension through:

### Adding New Agents

```python
from claudes_deep_coding.agents.base import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="custom",
            name="Custom Agent",
            description="My custom agent"
        )
    
    async def can_handle_task(self, task_data):
        # Implement task matching logic
        pass
    
    async def execute_task(self, task_data):
        # Implement task execution
        pass
```

### Custom Persistence Backends

The persistence interface can be implemented for:
- Different databases (PostgreSQL, MongoDB)
- Cloud storage (S3, Azure Blob)
- In-memory storage
- Custom solutions

### Enhanced Planning Algorithms

The planner can be extended with:
- Machine learning-based prioritization
- Intelligent task decomposition
- Resource-aware scheduling
- Deadline-driven planning

## Performance Considerations

### Async/Await

All agents use async/await for:
- Non-blocking I/O operations
- Concurrent task execution
- Efficient resource utilization

### Persistence Optimization

- SQLite with WAL mode for concurrent reads
- Batched writes for improved throughput
- Indexed queries for fast lookups
- Connection pooling for scalability

### Memory Management

- Pydantic models for validated, typed data
- Lazy loading of task history
- Efficient message queuing
- State cleanup on workflow completion

## Security Considerations

### State Isolation

- Each agent maintains isolated state
- No direct state sharing between agents
- Controlled communication via middleware

### Input Validation

- Pydantic models validate all inputs
- Type checking at runtime
- Schema enforcement

### Audit Trail

- Complete history of all actions
- Timestamped event logging
- Traceable task assignments

## Testing Strategy

The system includes:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-agent workflow testing
- **Persistence Tests**: State management validation
- **Middleware Tests**: Communication layer testing

All tests use pytest with async support.

## Future Enhancements

Potential improvements include:

1. **LLM Integration**: Connect to actual LLMs (Claude, GPT-4)
2. **Real Code Execution**: Execute generated code in sandboxed environments
3. **Advanced Planning**: ML-based task optimization
4. **Monitoring UI**: Web interface for workflow visualization
5. **Agent Learning**: Capture and reuse successful patterns
6. **Multi-Repository**: Work across multiple codebases
7. **Collaboration**: Multiple orchestrators working together
8. **Plugin System**: Easy addition of custom agents and capabilities

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
