#!/usr/bin/env python3
"""
Example demonstrating ChromaDB memory usage for deepagents.

This script shows how to:
1. Initialize the ChromaDB memory system
2. Store code snippets, tasks, and error solutions
3. Query the memory for relevant information
"""

import logging
from pathlib import Path

from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory
from deepagents.utils import format_code_context, format_task_summary

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Run the example demonstration."""
    logger.info("=== ChromaDB Memory Demo for Deepagents ===\n")

    # Initialize ChromaDB manager
    logger.info("Initializing ChromaDB...")
    chroma_manager = ChromaMemoryManager(
        persist_directory=config.chromadb.persist_directory,
        collection_name=config.chromadb.collection_name,
    )

    # Initialize coding memory
    coding_memory = CodingMemory(chroma_manager)

    # Example 1: Store code snippets
    logger.info("\n--- Example 1: Storing Code Snippets ---")

    snippet1_id = coding_memory.store_code_snippet(
        code="""
def fibonacci(n: int) -> int:
    '''Calculate the nth Fibonacci number using recursion.'''
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
""",
        language="python",
        description="Recursive Fibonacci implementation",
        tags=["algorithm", "recursion", "fibonacci"],
        file_path="algorithms/fibonacci.py",
    )
    logger.info(f"Stored snippet 1: {snippet1_id}")

    snippet2_id = coding_memory.store_code_snippet(
        code="""
async def fetch_data(url: str) -> dict:
    '''Fetch JSON data from an API endpoint.'''
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
""",
        language="python",
        description="Async function to fetch data from API",
        tags=["async", "http", "api"],
        file_path="utils/api.py",
    )
    logger.info(f"Stored snippet 2: {snippet2_id}")

    # Example 2: Store task context
    logger.info("\n--- Example 2: Storing Task Context ---")

    task1_id = coding_memory.store_task_context(
        task_description="Implemented user authentication system with JWT tokens",
        task_type="feature",
        files_involved=["auth/jwt.py", "middleware/auth.py", "models/user.py"],
        dependencies=["pyjwt", "passlib"],
        outcomes="Successfully added JWT-based authentication with password hashing",
    )
    logger.info(f"Stored task 1: {task1_id}")

    # Example 3: Store error solutions
    logger.info("\n--- Example 3: Storing Error Solutions ---")

    error1_id = coding_memory.store_error_solution(
        error_message="ModuleNotFoundError: No module named 'chromadb'",
        solution="Install chromadb using: pip install chromadb",
        error_type="dependency",
        language="python",
    )
    logger.info(f"Stored error solution 1: {error1_id}")

    # Example 4: Query for similar code
    logger.info("\n--- Example 4: Querying for Similar Code ---")

    results = coding_memory.find_similar_code(
        query="how to implement a recursive algorithm",
        n_results=2,
    )

    logger.info(f"Found {len(results)} similar code snippets")
    print(format_code_context(results))

    # Example 5: Query for similar tasks
    logger.info("\n--- Example 5: Querying for Similar Tasks ---")

    task_results = coding_memory.find_similar_tasks(
        query="authentication implementation",
        n_results=2,
    )

    logger.info(f"Found {len(task_results)} similar tasks")
    print(format_task_summary(task_results))

    # Example 6: Query for error solutions
    logger.info("\n--- Example 6: Querying for Error Solutions ---")

    error_results = coding_memory.find_error_solutions(
        error_query="module not found error",
        n_results=2,
    )

    logger.info(f"Found {len(error_results)} similar error solutions")
    for i, result in enumerate(error_results, 1):
        print(f"\n--- Solution {i} ---")
        print(result["document"])

    # Show memory statistics
    logger.info(f"\n--- Memory Statistics ---")
    logger.info(f"Total items in memory: {chroma_manager.count()}")

    logger.info("\n=== Demo Complete ===")
    logger.info(
        "The ChromaDB data has been persisted and will be available in future runs."
    )


if __name__ == "__main__":
    main()
