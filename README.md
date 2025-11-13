# claudes_deep_coding

The infamous langchain-ai (based) deepagents designed around Claude code agents/sub-agents for deeper work and help coding.

## Features

- **ChromaDB Integration**: Long-term memory and RAG capabilities for coding agents
- **Coding Memory Management**: Store and retrieve code snippets, task contexts, and error solutions
- **Semantic Search**: Find relevant information using vector similarity search
- **Persistent Storage**: All memories are stored persistently and available across sessions

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or your preferred package manager

### Install Dependencies

```bash
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your configuration:
   ```bash
   # Anthropic API Key for Claude
   ANTHROPIC_API_KEY=your_api_key_here
   
   # ChromaDB Configuration
   CHROMA_PERSIST_DIRECTORY=./chroma_db
   CHROMA_COLLECTION_NAME=deepagents_memory
   ```

## Usage

### Basic Example

```python
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory

# Initialize ChromaDB
chroma_manager = ChromaMemoryManager(
    persist_directory=config.chromadb.persist_directory,
    collection_name=config.chromadb.collection_name,
)

# Initialize coding memory
coding_memory = CodingMemory(chroma_manager)

# Store a code snippet
snippet_id = coding_memory.store_code_snippet(
    code="def hello_world():\n    print('Hello, World!')",
    language="python",
    description="Simple hello world function",
    tags=["example", "basic"],
)

# Find similar code
results = coding_memory.find_similar_code(
    query="how to print hello world",
    n_results=5,
)

for result in results:
    print(f"Code: {result['document']}")
    print(f"Language: {result['metadata']['language']}")
```

### Running the Demo

Run the included example to see ChromaDB in action:

```bash
python examples/basic_usage.py
```

This will demonstrate:
- Storing code snippets with metadata
- Storing task contexts
- Storing error solutions
- Querying for similar code, tasks, and errors
- Persistent storage across runs

## ChromaDB Memory Features

### Store Code Snippets

```python
coding_memory.store_code_snippet(
    code="your code here",
    language="python",
    description="What the code does",
    tags=["tag1", "tag2"],
    file_path="path/to/file.py",
    project="project_name",
)
```

### Store Task Context

```python
coding_memory.store_task_context(
    task_description="Description of what was done",
    task_type="feature",  # or "bug_fix", "refactor", etc.
    files_involved=["file1.py", "file2.py"],
    dependencies=["package1", "package2"],
    outcomes="What was accomplished",
)
```

### Store Error Solutions

```python
coding_memory.store_error_solution(
    error_message="The error message",
    solution="How to fix it",
    error_type="runtime",
    language="python",
)
```

### Query Memory

```python
# Find similar code
results = coding_memory.find_similar_code(
    query="authentication implementation",
    language="python",  # optional filter
    n_results=5,
)

# Find similar tasks
task_results = coding_memory.find_similar_tasks(
    query="user authentication",
    task_type="feature",  # optional filter
    n_results=5,
)

# Find error solutions
error_results = coding_memory.find_error_solutions(
    error_query="import error",
    language="python",  # optional filter
    n_results=5,
)
```

## Architecture

```
src/deepagents/
├── config/           # Configuration management
├── memory/           # ChromaDB memory management
│   ├── chroma_manager.py   # Low-level ChromaDB operations
│   └── coding_memory.py    # Coding-specific memory operations
└── utils/            # Utility functions
    └── memory_utils.py     # Memory formatting utilities
```

## Development

### Code Formatting

```bash
black src/ examples/
```

### Linting

```bash
ruff check src/ examples/
```

### Running Tests

```bash
pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
