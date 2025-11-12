# Contributing to Claudes Deep Coding

Thank you for your interest in contributing to Claudes Deep Coding! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claudes_deep_coding.git
   cd claudes_deep_coding
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   # or
   pip install -r requirements-dev.txt
   ```

4. Start Neo4j:
   ```bash
   docker-compose up -d
   ```

5. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Code Style

We use:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **mypy** for type checking

Before submitting a PR, run:

```bash
# Format code
black deepagents/ tests/ examples/

# Lint
ruff check deepagents/ tests/ examples/

# Type check
mypy deepagents/
```

## Testing

We use pytest for testing. Write tests for all new features.

Run tests:
```bash
# All tests
pytest

# With coverage
pytest --cov=deepagents --cov-report=html

# Specific test file
pytest tests/test_deepagent.py

# Specific test
pytest tests/test_deepagent.py::test_deep_agent_init
```

### Test Guidelines

- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (Neo4j, LLM calls)
- Use pytest fixtures for common setups
- Aim for >80% code coverage

## Pull Request Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

3. Write or update tests

4. Ensure all tests pass and code is formatted:
   ```bash
   pytest
   black deepagents/ tests/ examples/
   ruff check deepagents/ tests/ examples/
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request on GitHub

### PR Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include tests for new functionality
- Update documentation if needed
- Keep PRs focused on a single feature/fix

## Commit Message Format

Use clear, descriptive commit messages:

```
Add: new feature or functionality
Fix: bug fix
Update: changes to existing features
Docs: documentation changes
Test: test additions or changes
Refactor: code refactoring
```

Examples:
- `Add: support for custom Neo4j databases`
- `Fix: connection timeout in Neo4jManager`
- `Update: improve search performance`
- `Docs: add example for multi-project setup`

## Code Organization

```
deepagents/
├── __init__.py          # Package exports
├── config.py            # Configuration management
├── neo4j_manager.py     # Neo4j connection handling
├── knowledge_graph.py   # Knowledge graph operations
└── deepagent.py         # Main agent implementation

tests/
├── test_config.py
├── test_neo4j_manager.py
├── test_knowledge_graph.py
└── test_deepagent.py

examples/
├── basic_usage.py
└── advanced_analysis.py
```

## Adding New Features

When adding new features:

1. **Design First**: Open an issue to discuss the feature
2. **Documentation**: Update README and docstrings
3. **Tests**: Write comprehensive tests
4. **Examples**: Add usage examples if applicable
5. **Type Hints**: Use type hints for all functions
6. **Logging**: Add appropriate logging statements

## Issues and Bug Reports

When reporting issues:

- Use a clear, descriptive title
- Provide steps to reproduce
- Include error messages and stack traces
- Specify your environment (OS, Python version, etc.)
- Mention Neo4j version if relevant

## Questions?

- Open an issue with the `question` label
- Check existing issues and documentation first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
