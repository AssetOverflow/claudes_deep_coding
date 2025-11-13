"""Tests for ChromaDB memory management."""

import pytest

from deepagents.memory import ChromaMemoryManager, CodingMemory


@pytest.fixture
def chroma_manager():
    """Create an in-memory ChromaDB manager for testing."""
    manager = ChromaMemoryManager(
        persist_directory=None,  # Use in-memory for tests
        collection_name="test_collection",
    )
    yield manager
    # Cleanup
    manager.clear()


@pytest.fixture
def coding_memory(chroma_manager):
    """Create a CodingMemory instance for testing."""
    return CodingMemory(chroma_manager)


class TestChromaMemoryManager:
    """Test ChromaDB manager functionality."""

    def test_add_and_count(self, chroma_manager):
        """Test adding documents and counting."""
        assert chroma_manager.count() == 0

        chroma_manager.add_memory(
            documents=["Test document 1", "Test document 2"],
            metadatas=[{"type": "test"}, {"type": "test"}],
        )

        assert chroma_manager.count() == 2

    def test_query_memory(self, chroma_manager):
        """Test querying for similar documents."""
        chroma_manager.add_memory(
            documents=["Python programming language", "JavaScript is used for web development"],
            metadatas=[{"lang": "python"}, {"lang": "javascript"}],
        )

        results = chroma_manager.query_memory(
            query_texts=["scripting language"],
            n_results=2,
        )

        assert len(results["ids"][0]) == 2
        assert len(results["documents"][0]) == 2

    def test_get_by_id(self, chroma_manager):
        """Test retrieving documents by ID."""
        chroma_manager.add_memory(
            documents=["Test document"],
            metadatas=[{"type": "test"}],
            ids=["test-id-1"],
        )

        results = chroma_manager.get_memory_by_id(ids=["test-id-1"])

        assert len(results["ids"]) == 1
        assert results["ids"][0] == "test-id-1"
        assert results["documents"][0] == "Test document"

    def test_update_memory(self, chroma_manager):
        """Test updating existing documents."""
        chroma_manager.add_memory(
            documents=["Original document"],
            metadatas=[{"version": "1"}],
            ids=["doc-1"],
        )

        chroma_manager.update_memory(
            ids=["doc-1"],
            documents=["Updated document"],
            metadatas=[{"version": "2"}],
        )

        results = chroma_manager.get_memory_by_id(ids=["doc-1"])
        assert results["documents"][0] == "Updated document"
        assert results["metadatas"][0]["version"] == "2"

    def test_delete_memory(self, chroma_manager):
        """Test deleting documents."""
        chroma_manager.add_memory(
            documents=["Document to delete"],
            ids=["delete-me"],
        )

        assert chroma_manager.count() == 1

        chroma_manager.delete_memory(ids=["delete-me"])

        assert chroma_manager.count() == 0

    def test_clear(self, chroma_manager):
        """Test clearing all documents."""
        chroma_manager.add_memory(
            documents=["Doc 1", "Doc 2", "Doc 3"],
        )

        assert chroma_manager.count() == 3

        chroma_manager.clear()

        assert chroma_manager.count() == 0


class TestCodingMemory:
    """Test coding-specific memory functionality."""

    def test_store_code_snippet(self, coding_memory, chroma_manager):
        """Test storing a code snippet."""
        snippet_id = coding_memory.store_code_snippet(
            code="def test():\n    pass",
            language="python",
            description="Test function",
            tags=["test", "example"],
        )

        assert snippet_id.startswith("code_")
        assert chroma_manager.count() == 1

    def test_store_task_context(self, coding_memory, chroma_manager):
        """Test storing task context."""
        task_id = coding_memory.store_task_context(
            task_description="Fixed bug in authentication",
            task_type="bug_fix",
            files_involved=["auth.py"],
        )

        assert task_id.startswith("task_")
        assert chroma_manager.count() == 1

    def test_store_error_solution(self, coding_memory, chroma_manager):
        """Test storing an error solution."""
        error_id = coding_memory.store_error_solution(
            error_message="ImportError: No module named 'foo'",
            solution="Install the module: pip install foo",
            error_type="import",
        )

        assert error_id.startswith("error_")
        assert chroma_manager.count() == 1

    def test_find_similar_code(self, coding_memory):
        """Test finding similar code snippets."""
        coding_memory.store_code_snippet(
            code="def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
            language="python",
            description="Recursive fibonacci",
            tags=["algorithm", "recursion"],
        )

        coding_memory.store_code_snippet(
            code="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
            language="python",
            description="Recursive factorial",
            tags=["algorithm", "recursion"],
        )

        results = coding_memory.find_similar_code(
            query="recursive algorithm implementation",
            n_results=2,
        )

        assert len(results) == 2
        assert all("algorithm" in r["metadata"].get("tags", []) for r in results)

    def test_find_similar_tasks(self, coding_memory):
        """Test finding similar tasks."""
        coding_memory.store_task_context(
            task_description="Implemented user authentication with JWT",
            task_type="feature",
            files_involved=["auth.py", "jwt.py"],
        )

        coding_memory.store_task_context(
            task_description="Added password reset functionality",
            task_type="feature",
            files_involved=["auth.py", "email.py"],
        )

        results = coding_memory.find_similar_tasks(
            query="user authentication system",
            n_results=2,
        )

        assert len(results) == 2
        assert all(r["metadata"]["type"] == "task_context" for r in results)

    def test_find_error_solutions(self, coding_memory):
        """Test finding error solutions."""
        coding_memory.store_error_solution(
            error_message="ModuleNotFoundError: No module named 'requests'",
            solution="Install requests: pip install requests",
            error_type="dependency",
            language="python",
        )

        results = coding_memory.find_error_solutions(
            error_query="module not found",
            n_results=1,
        )

        assert len(results) == 1
        assert "ModuleNotFoundError" in results[0]["document"]

    def test_filter_by_language(self, coding_memory):
        """Test filtering code snippets by language."""
        coding_memory.store_code_snippet(
            code="def test(): pass",
            language="python",
            description="Python test",
        )

        coding_memory.store_code_snippet(
            code="function test() {}",
            language="javascript",
            description="JavaScript test",
        )

        python_results = coding_memory.find_similar_code(
            query="test function",
            language="python",
            n_results=5,
        )

        assert len(python_results) == 1
        assert python_results[0]["metadata"]["language"] == "python"

    def test_filter_by_task_type(self, coding_memory):
        """Test filtering tasks by type."""
        coding_memory.store_task_context(
            task_description="Fixed authentication bug",
            task_type="bug_fix",
        )

        coding_memory.store_task_context(
            task_description="Added new authentication feature",
            task_type="feature",
        )

        bug_fix_results = coding_memory.find_similar_tasks(
            query="authentication",
            task_type="bug_fix",
            n_results=5,
        )

        assert len(bug_fix_results) == 1
        assert bug_fix_results[0]["metadata"]["task_type"] == "bug_fix"
