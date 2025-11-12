# Contributing to Claudes Deep Coding

Thank you for your interest in contributing to the Claudes Deep Coding project! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/claudes_deep_coding.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push
7. Open a Pull Request

## Development Setup

### Install Dependencies

```bash
# Install in development mode
pip install -e ".[dev]"

# Or using requirements.txt
pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# ANTHROPIC_API_KEY=your_key_here
```

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:
- Maximum line length: 100 characters
- Use double quotes for strings
- Use type hints where appropriate

### Code Formatting

Format your code with Black:
```bash
black src/ tests/ examples/
```

### Linting

Check your code with Ruff:
```bash
ruff check src/ tests/ examples/
```

### Type Checking

We encourage (but don't require) type hints:
```python
def store_code_snippet(
    self,
    code: str,
    language: str,
    description: str,
    tags: Optional[List[str]] = None,
) -> str:
    ...
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=deepagents --cov-report=html

# Run specific test file
pytest tests/test_memory.py

# Run specific test
pytest tests/test_memory.py::TestCodingMemory::test_store_code_snippet
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Test both success and failure cases

Example:
```python
def test_store_code_snippet(coding_memory, chroma_manager):
    """Test storing a code snippet."""
    snippet_id = coding_memory.store_code_snippet(
        code="def test(): pass",
        language="python",
        description="Test function",
    )
    
    assert snippet_id.startswith("code_")
    assert chroma_manager.count() == 1
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def find_similar_code(
    self,
    query: str,
    language: Optional[str] = None,
    n_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Find similar code snippets.

    Args:
        query: Query string describing what to look for
        language: Optional filter by programming language
        n_results: Number of results to return

    Returns:
        List of similar code snippets with metadata

    Raises:
        ValueError: If query is empty
    """
```

### Comments

- Write self-documenting code when possible
- Add comments for complex logic
- Explain *why*, not *what*

Good comment:
```python
# Use batch operations for better performance with large datasets
chroma_manager.add_memory(documents=documents, metadatas=metadatas)
```

Poor comment:
```python
# Add documents to memory
chroma_manager.add_memory(documents=documents, metadatas=metadatas)
```

### Documentation Files

- Keep README.md up to date
- Update relevant .md files in the docs
- Add examples for new features

## Pull Request Process

### Before Submitting

1. ✅ Run tests: `pytest`
2. ✅ Format code: `black src/ tests/ examples/`
3. ✅ Lint code: `ruff check src/ tests/ examples/`
4. ✅ Update documentation
5. ✅ Add/update tests for new features
6. ✅ Update CHANGELOG.md if applicable

### PR Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what and why
- **Link issues**: Reference related issues
- **Small PRs**: Keep changes focused
- **Tests**: Include tests for new features
- **Documentation**: Update docs as needed

Example PR description:
```markdown
## Description
Adds support for batch operations in ChromaMemoryManager to improve performance when storing large numbers of code snippets.

## Changes
- Added `add_batch()` method to ChromaMemoryManager
- Updated CodingMemory to use batch operations when appropriate
- Added tests for batch operations
- Updated documentation

## Related Issues
Fixes #123

## Testing
- [ ] Added unit tests
- [ ] Tested with 1000+ documents
- [ ] Verified backward compatibility
```

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Search existing issues
3. Create a new issue with:
   - Clear description
   - Use cases
   - Expected behavior
   - Example code (if applicable)

## Bug Reports

When reporting bugs, please include:

1. **Description**: What happened vs. what you expected
2. **Environment**: Python version, OS, package versions
3. **Reproduction**: Steps to reproduce
4. **Code**: Minimal code example
5. **Error**: Full error message/traceback

Example:
```markdown
## Bug Description
ChromaMemoryManager fails to initialize when persist_directory doesn't exist

## Environment
- Python: 3.10.5
- OS: Ubuntu 22.04
- chromadb: 0.4.22

## Steps to Reproduce
1. Set CHROMA_PERSIST_DIRECTORY to non-existent path
2. Initialize ChromaMemoryManager
3. Error occurs

## Code Example
\```python
manager = ChromaMemoryManager(
    persist_directory=Path("/non/existent/path"),
)
\```

## Error
\```
FileNotFoundError: /non/existent/path does not exist
\```

## Expected Behavior
Should create the directory automatically
```

## Code Review

We review all PRs. Expect:
- Constructive feedback
- Requests for changes
- Discussion on approach

Please:
- Be patient
- Be respectful
- Address feedback
- Ask questions if unclear

## Areas for Contribution

### High Priority
- Additional embedding function support
- Performance optimizations
- More comprehensive tests
- Documentation improvements

### Good First Issues
- Add type hints to existing code
- Improve error messages
- Add examples for specific use cases
- Documentation fixes

### Advanced Features
- LangChain integration examples
- Support for multiple vector stores
- Agent workflow templates
- Performance benchmarking tools

## Community

- Be respectful and inclusive
- Help others
- Share knowledge
- Collaborate openly

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for technical questions
- Use discussions for general questions
- Check existing issues and PRs first

Thank you for contributing! 🎉
