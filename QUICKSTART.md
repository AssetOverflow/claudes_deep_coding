# Quick Start Guide

Get started with ChromaDB memory for deepagents in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/AssetOverflow/claudes_deep_coding.git
cd claudes_deep_coding

# Install dependencies
pip install -r requirements.txt
```

Or with pip:
```bash
pip install -e .
```

## Configuration

1. Create a `.env` file:
```bash
cp .env.example .env
```

2. Add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Basic Usage

### 1. Initialize the System

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
```

### 2. Store Information

**Store a code snippet:**
```python
coding_memory.store_code_snippet(
    code="def hello_world():\n    print('Hello, World!')",
    language="python",
    description="Simple hello world function",
    tags=["example", "basic"],
)
```

**Store a task:**
```python
coding_memory.store_task_context(
    task_description="Added user authentication",
    task_type="feature",
    files_involved=["auth.py", "models.py"],
)
```

**Store an error solution:**
```python
coding_memory.store_error_solution(
    error_message="ModuleNotFoundError: No module named 'chromadb'",
    solution="Install chromadb: pip install chromadb",
)
```

### 3. Query Information

**Find similar code:**
```python
results = coding_memory.find_similar_code(
    query="how to print hello world",
    n_results=5,
)

for result in results:
    print(result['document'])
```

**Find similar tasks:**
```python
results = coding_memory.find_similar_tasks(
    query="user authentication",
    n_results=3,
)
```

**Find error solutions:**
```python
results = coding_memory.find_error_solutions(
    error_query="module not found",
    n_results=3,
)
```

## Run the Demo

```bash
python examples/basic_usage.py
```

This will:
- Store example code snippets, tasks, and errors
- Query for similar items
- Display formatted results
- Show memory statistics

## Next Steps

- Read the full [ChromaDB Setup Documentation](CHROMADB_SETUP.md)
- Explore the [examples](examples/) directory
- Check out the [source code](src/deepagents/)
- Run the [tests](tests/) with `pytest`

## Common Issues

**Q: Where is my data stored?**  
A: By default in `./chroma_db/`. Configure via `CHROMA_PERSIST_DIRECTORY` in `.env`.

**Q: How do I clear all data?**  
A: Use `chroma_manager.clear()` or delete the `chroma_db/` directory.

**Q: Can I use a different embedding model?**  
A: Yes! See [Advanced Usage](CHROMADB_SETUP.md#advanced-usage) in the documentation.
