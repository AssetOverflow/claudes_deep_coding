# Claudes Deep Coding

The infamous LangChain-AI based deepagents designed around Claude Code agents/sub-agents for deeper work and coding assistance, now with **dynamic knowledge graph integration** using Neo4j and Graphiti.

## Overview

Claudes Deep Coding provides a framework for building intelligent coding agents that maintain dynamic knowledge graphs of your projects and conversations. The knowledge graph is dynamically created and updated by deepagents powered by Claude, enabling deeper understanding of codebases and more contextual assistance.

### Key Features

- 🧠 **Dynamic Knowledge Graph**: Automatically builds and maintains a knowledge graph of your projects
- 🤖 **LLM-Powered Analysis**: Uses Claude to understand code and conversations
- 📊 **Neo4j Integration**: Persistent graph database for complex relationship queries
- 🔄 **Graphiti Integration**: Advanced knowledge graph management
- 🎯 **Context-Aware**: Maintains conversation history and project context
- 🔍 **Smart Search**: Query your knowledge graph with natural language
- 📈 **Adaptive Learning**: Knowledge graph evolves with your conversations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        DeepAgent                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Claude LLM (Conversation Analysis)          │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Knowledge Graph Manager (Graphiti)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Neo4j Database (Graph Storage)              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker (for Neo4j)
- Neo4j 5.14+ (can be run via Docker)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/AssetOverflow/claudes_deep_coding.git
cd claudes_deep_coding
```

2. Install dependencies:
```bash
pip install -e .
```

For development with testing tools:
```bash
pip install -e ".[dev]"
```

3. Start Neo4j using Docker:
```bash
docker-compose up -d
```

This will start Neo4j with:
- HTTP interface: http://localhost:7474
- Bolt connection: bolt://localhost:7687
- Default credentials: neo4j/deepcoding123

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
- `NEO4J_URI`: Neo4j connection URI (default: bolt://localhost:7687)
- `NEO4J_USERNAME`: Neo4j username (default: neo4j)
- `NEO4J_PASSWORD`: Neo4j password
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional, for Claude integration)

## Quick Start

### Basic Usage

```python
import asyncio
from deepagents import DeepAgent

async def main():
    # Initialize the agent
    agent = DeepAgent()
    await agent.initialize()
    
    # Set up a project
    await agent.set_project(
        project_name="my_awesome_project",
        description="A web application using FastAPI"
    )
    
    # Process a conversation
    response = await agent.process_message(
        message="I need to implement user authentication",
        context={"feature": "auth", "framework": "fastapi"}
    )
    
    # Search the knowledge graph
    results = await agent.search_knowledge("authentication patterns")
    
    # Get project summary
    summary = await agent.get_project_summary()
    print(f"Nodes: {summary['stats']['nodes']}")
    print(f"Relationships: {summary['stats']['relationships']}")
    
    await agent.close()

asyncio.run(main())
```

### Adding Code Entities

```python
# Add a file entity
await agent.knowledge_graph.add_code_entity(
    entity_type="File",
    name="auth.py",
    properties={
        "path": "/src/auth.py",
        "language": "python"
    }
)

# Add a class with relationships
await agent.knowledge_graph.add_code_entity(
    entity_type="Class",
    name="UserService",
    properties={
        "description": "Handles user operations"
    },
    relationships=[
        {"target_name": "auth.py", "relationship_type": "DEFINED_IN"}
    ]
)
```

## Examples

Check out the `examples/` directory for more detailed examples:

- `basic_usage.py`: Simple demonstration of core features
- `advanced_analysis.py`: Analyzing an entire codebase and building a comprehensive knowledge graph

Run examples:
```bash
python examples/basic_usage.py
python examples/advanced_analysis.py
```

## Development

### Running Tests

```bash
pytest tests/
```

With coverage:
```bash
pytest --cov=deepagents tests/
```

### Code Formatting

```bash
black deepagents/ tests/ examples/
```

### Linting

```bash
ruff check deepagents/ tests/ examples/
```

## Knowledge Graph Schema

The system creates the following node types:

- **Project**: Represents a software project
- **File**: Source code files
- **Function**: Function/method definitions
- **Class**: Class definitions
- **Module**: Code modules/packages
- **Conversation**: Conversation episodes
- **Entity**: Generic entities extracted from conversations

Common relationships:
- `CONTAINS`: Project contains files
- `DEFINED_IN`: Code entity defined in a file
- `CALLS`: Function calls another function
- `INHERITS`: Class inheritance
- `IMPORTS`: Module imports
- `RELATES_TO`: Generic relationship between entities

## Neo4j Browser

Access the Neo4j browser at http://localhost:7474 to visualize your knowledge graph.

Example Cypher queries:

```cypher
// View all projects
MATCH (p:Project) RETURN p

// View project structure
MATCH (p:Project {name: 'my_project'})-[:CONTAINS]->(f:File)
RETURN p, f

// Find all functions in a file
MATCH (f:File {name: 'auth.py'})-[:DEFINES]->(fn:Function)
RETURN fn

// View conversation history
MATCH (c:Conversation)
RETURN c ORDER BY c.timestamp DESC LIMIT 10
```

## Configuration

Configuration can be provided via:
1. Environment variables (`.env` file)
2. Direct instantiation of `DeepAgentConfig`
3. Default values

Available configuration options:

```python
from deepagents import DeepAgentConfig

config = DeepAgentConfig(
    neo4j_uri="bolt://localhost:7687",
    neo4j_username="neo4j",
    neo4j_password="your_password",
    anthropic_api_key="your_api_key",
    max_iterations=10,
    conversation_memory_window=20
)
```

## API Reference

### DeepAgent

Main agent class for interacting with the knowledge graph.

**Methods:**
- `initialize()`: Initialize the agent and knowledge graph
- `process_message(message, context)`: Process a conversation message
- `set_project(name, description)`: Set the current project
- `search_knowledge(query, limit)`: Search the knowledge graph
- `get_project_summary()`: Get project statistics and context
- `close()`: Close connections and cleanup

### KnowledgeGraphManager

Manages the knowledge graph using Graphiti and Neo4j.

**Methods:**
- `initialize()`: Initialize Graphiti
- `add_conversation_episode(content, metadata)`: Add conversation to graph
- `add_code_entity(type, name, properties, relationships)`: Add code entity
- `search_knowledge(query, limit)`: Search for information
- `get_project_context(project_name)`: Get project details
- `add_project(name, description, metadata)`: Add a new project

### Neo4jManager

Low-level Neo4j connection management.

**Methods:**
- `connect()`: Connect to Neo4j
- `close()`: Close connection
- `execute_query(query, parameters)`: Execute Cypher query
- `create_indexes()`: Create necessary indexes
- `get_stats()`: Get database statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Anthropic's Claude](https://www.anthropic.com/)
- Graph database by [Neo4j](https://neo4j.com/)
- Knowledge graph management by [Graphiti](https://github.com/getzep/graphiti)
