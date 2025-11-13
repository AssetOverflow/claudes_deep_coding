# ChromaDB Setup for Deepagents

This document provides detailed information about the ChromaDB integration in the deepagents system.

## Overview

ChromaDB is used to provide long-term memory and Retrieval-Augmented Generation (RAG) capabilities for the deepagents coding system. It stores:

- **Code snippets** with metadata (language, description, tags, file paths)
- **Task contexts** (what was done, files involved, outcomes)
- **Error solutions** (errors encountered and how they were fixed)

All data is persisted locally and available across sessions, allowing agents to learn from past experiences.

## Architecture

### Components

1. **ChromaMemoryManager** (`src/deepagents/memory/chroma_manager.py`)
   - Low-level interface to ChromaDB
   - Handles connection, collection management
   - Provides basic CRUD operations
   - Supports both local persistent and client/server modes

2. **CodingMemory** (`src/deepagents/memory/coding_memory.py`)
   - High-level interface for coding-specific operations
   - Stores and retrieves code snippets, tasks, and error solutions
   - Provides semantic search capabilities
   - Formats metadata appropriately for each type of memory

3. **Configuration** (`src/deepagents/config/__init__.py`)
   - Manages settings via environment variables
   - Configurable persistence directory, collection name
   - Optional client/server mode configuration

### Data Flow

```
User/Agent
    ↓
CodingMemory (high-level API)
    ↓
ChromaMemoryManager (low-level API)
    ↓
ChromaDB (vector database)
    ↓
Persistent Storage (./chroma_db)
```

## Storage Types

### Code Snippets

Store code with rich metadata for later retrieval.

**Metadata:**
- `type`: "code_snippet"
- `language`: Programming language
- `description`: What the code does
- `tags`: List of tags (stored as JSON)
- `file_path`: Optional path to the file
- `project`: Optional project name
- `timestamp`: When it was stored

**Example:**
```python
snippet_id = coding_memory.store_code_snippet(
    code='''
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
    ''',
    language="python",
    description="Binary search implementation",
    tags=["algorithm", "search", "binary-search"],
    file_path="algorithms/search.py",
)
```

### Task Contexts

Store information about coding tasks completed.

**Metadata:**
- `type`: "task_context"
- `task_type`: Type of task (feature, bug_fix, refactor, etc.)
- `files_involved`: List of files (stored as JSON)
- `dependencies`: List of dependencies (stored as JSON)
- `outcomes`: What was accomplished
- `timestamp`: When it was stored

**Example:**
```python
task_id = coding_memory.store_task_context(
    task_description="Implemented caching layer for API responses using Redis",
    task_type="feature",
    files_involved=["api/cache.py", "api/client.py", "config/redis.py"],
    dependencies=["redis", "hiredis"],
    outcomes="Reduced API response time by 60% for cached endpoints",
)
```

### Error Solutions

Store errors encountered and their solutions.

**Metadata:**
- `type`: "error_solution"
- `error_message`: The original error message
- `error_type`: Type of error (syntax, runtime, logic, dependency, etc.)
- `language`: Programming language
- `timestamp`: When it was stored

**Example:**
```python
error_id = coding_memory.store_error_solution(
    error_message="AttributeError: 'NoneType' object has no attribute 'get'",
    solution="Added null check before accessing the dictionary: if data is not None: value = data.get('key')",
    error_type="runtime",
    language="python",
)
```

## Querying Memory

### Semantic Search

ChromaDB uses vector embeddings to find semantically similar content, not just keyword matching.

**Finding Similar Code:**
```python
results = coding_memory.find_similar_code(
    query="how to sort a list efficiently",
    language="python",  # Optional filter
    n_results=5,
)

for result in results:
    print(f"Code: {result['document']}")
    print(f"Language: {result['metadata']['language']}")
    print(f"Similarity: {1 - result['distance']:.2f}")
```

**Finding Similar Tasks:**
```python
results = coding_memory.find_similar_tasks(
    query="implementing user authentication",
    task_type="feature",  # Optional filter
    n_results=3,
)
```

**Finding Error Solutions:**
```python
results = coding_memory.find_error_solutions(
    error_query="connection timeout error",
    language="python",  # Optional filter
    n_results=3,
)
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required for Claude integration
ANTHROPIC_API_KEY=sk-ant-...

# ChromaDB configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=deepagents_memory

# Optional: Client/Server mode
# CHROMA_HOST=localhost
# CHROMA_PORT=8000
```

### Modes of Operation

**1. Local Persistent Mode (Default)**
```python
chroma_manager = ChromaMemoryManager(
    persist_directory=Path("./chroma_db"),
    collection_name="deepagents_memory",
)
```

Data is stored locally in the specified directory and persisted across runs.

**2. In-Memory Mode (Testing)**
```python
chroma_manager = ChromaMemoryManager(
    persist_directory=None,
    collection_name="test_collection",
)
```

Data is stored in memory and lost when the process ends. Useful for testing.

**3. Client/Server Mode**
```python
chroma_manager = ChromaMemoryManager(
    host="localhost",
    port=8000,
    collection_name="deepagents_memory",
)
```

Connects to a ChromaDB server. Requires running a ChromaDB server separately.

## Best Practices

### 1. Meaningful Descriptions

Write clear descriptions for code and tasks:

**Good:**
```python
description="Recursive function to traverse a binary tree in-order (left, root, right)"
```

**Not as good:**
```python
description="Tree function"
```

### 2. Use Tags Effectively

Tags improve retrieval. Use consistent, meaningful tags:

```python
tags=["algorithm", "tree", "recursion", "dfs", "in-order"]
```

### 3. Store Context, Not Just Code

Include surrounding context when storing code:

```python
code='''
# User authentication endpoint
@app.post("/auth/login")
async def login(credentials: LoginCredentials):
    user = await authenticate_user(credentials)
    if user:
        return generate_jwt_token(user)
    raise HTTPException(status_code=401, detail="Invalid credentials")
'''
```

### 4. Regular Cleanup

Periodically review and update stored memories:

```python
# Get all items
results = chroma_manager.query_memory(
    query_texts=[""],
    n_results=1000,
)

# Delete outdated items
chroma_manager.delete_memory(ids=outdated_ids)
```

### 5. Metadata Consistency

Use consistent metadata keys and values:

```python
# Good: consistent task types
task_type="feature"  # or "bug_fix", "refactor", "optimization"

# Avoid: inconsistent task types
task_type="new feature"  # vs "Feature" vs "FEATURE"
```

## Integration with Deepagents

### In Agent Workflows

```python
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory

# Initialize
chroma_manager = ChromaMemoryManager(
    persist_directory=config.chromadb.persist_directory,
    collection_name=config.chromadb.collection_name,
)
coding_memory = CodingMemory(chroma_manager)

# When starting a new task, search for similar past work
similar_tasks = coding_memory.find_similar_tasks(
    query=current_task_description,
    n_results=3,
)

# Use the results to inform the agent's approach
for task in similar_tasks:
    print(f"Similar past task: {task['document']}")
    print(f"Outcome: {task['metadata'].get('outcomes')}")

# After completing the task, store the new context
coding_memory.store_task_context(
    task_description=current_task_description,
    task_type="feature",
    files_involved=modified_files,
    outcomes=task_results,
)
```

### Error Recovery

```python
try:
    # Attempt some operation
    result = risky_operation()
except Exception as e:
    # Search for similar errors
    solutions = coding_memory.find_error_solutions(
        error_query=str(e),
        language="python",
        n_results=3,
    )
    
    if solutions:
        print("Found similar errors:")
        for sol in solutions:
            print(f"Solution: {sol['document']}")
    
    # After fixing, store the solution
    coding_memory.store_error_solution(
        error_message=str(e),
        solution="Description of how it was fixed",
        error_type="runtime",
        language="python",
    )
```

## Troubleshooting

### Issue: ChromaDB not persisting data

**Solution:** Ensure the persist directory exists and is writable:
```python
persist_dir = Path("./chroma_db")
persist_dir.mkdir(parents=True, exist_ok=True)
```

### Issue: Query returns no results

**Possible causes:**
1. Collection is empty - add some data first
2. Query is too specific - try broader queries
3. Metadata filters are too restrictive

**Solution:** Check the collection count:
```python
print(f"Items in collection: {chroma_manager.count()}")
```

### Issue: Slow query performance

**Solutions:**
1. Reduce `n_results` parameter
2. Use metadata filters to narrow the search
3. Consider client/server mode for better performance

### Issue: Out of memory errors

**Solutions:**
1. Use client/server mode instead of local mode
2. Clear old/unused data periodically
3. Increase system memory

## Advanced Usage

### Custom Embedding Functions

You can use custom embedding functions:

```python
from chromadb.utils import embedding_functions

# Use OpenAI embeddings instead of default
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-api-key",
    model_name="text-embedding-ada-002"
)

collection = client.get_or_create_collection(
    name="custom_collection",
    embedding_function=openai_ef,
)
```

### Batch Operations

For better performance with large datasets:

```python
# Store multiple items at once
documents = [snippet1, snippet2, snippet3]
metadatas = [meta1, meta2, meta3]
ids = [id1, id2, id3]

chroma_manager.add_memory(
    documents=documents,
    metadatas=metadatas,
    ids=ids,
)
```

### Metadata Filtering

Use complex metadata queries:

```python
# Find Python code snippets with specific tags
results = chroma_manager.query_memory(
    query_texts=["sorting algorithm"],
    n_results=10,
    where={
        "$and": [
            {"language": "python"},
            {"type": "code_snippet"}
        ]
    },
)
```

## Performance Considerations

- **Embeddings:** Generated on first add, cached thereafter
- **Storage:** ~1KB per code snippet on average
- **Query Time:** ~10-50ms for typical queries
- **Indexing:** Automatic, handled by ChromaDB
- **Scalability:** Handles millions of documents efficiently

## Further Reading

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LangChain Integration](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
