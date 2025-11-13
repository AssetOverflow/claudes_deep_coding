"""Coding-specific memory management for deepagents."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .chroma_manager import ChromaMemoryManager

logger = logging.getLogger(__name__)


class CodingMemory:
    """Manages coding-specific memories for deepagents."""

    def __init__(self, chroma_manager: ChromaMemoryManager):
        """
        Initialize coding memory.

        Args:
            chroma_manager: ChromaDB manager instance
        """
        self.manager = chroma_manager

    def store_code_snippet(
        self,
        code: str,
        language: str,
        description: str,
        tags: Optional[List[str]] = None,
        file_path: Optional[str] = None,
        project: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a code snippet with metadata.

        Args:
            code: The code snippet
            language: Programming language
            description: Description of what the code does
            tags: Optional tags for categorization
            file_path: Optional file path where code is located
            project: Optional project name
            metadata: Additional metadata

        Returns:
            ID of the stored snippet
        """
        import uuid

        snippet_id = f"code_{uuid.uuid4()}"

        # Prepare metadata
        meta = {
            "type": "code_snippet",
            "language": language,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if tags:
            meta["tags"] = json.dumps(tags)
        if file_path:
            meta["file_path"] = file_path
        if project:
            meta["project"] = project
        if metadata:
            meta.update(metadata)

        # Store the code snippet
        self.manager.add_memory(
            documents=[code],
            metadatas=[meta],
            ids=[snippet_id],
        )

        logger.info(f"Stored code snippet: {snippet_id}")
        return snippet_id

    def store_task_context(
        self,
        task_description: str,
        task_type: str,
        files_involved: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        outcomes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store context about a coding task.

        Args:
            task_description: Description of the task
            task_type: Type of task (e.g., bug_fix, feature, refactor)
            files_involved: List of files involved in the task
            dependencies: List of dependencies added/modified
            outcomes: Outcomes or results of the task
            metadata: Additional metadata

        Returns:
            ID of the stored task context
        """
        import uuid

        task_id = f"task_{uuid.uuid4()}"

        # Prepare metadata
        meta = {
            "type": "task_context",
            "task_type": task_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if files_involved:
            meta["files_involved"] = json.dumps(files_involved)
        if dependencies:
            meta["dependencies"] = json.dumps(dependencies)
        if outcomes:
            meta["outcomes"] = outcomes
        if metadata:
            meta.update(metadata)

        # Store the task context
        self.manager.add_memory(
            documents=[task_description],
            metadatas=[meta],
            ids=[task_id],
        )

        logger.info(f"Stored task context: {task_id}")
        return task_id

    def store_error_solution(
        self,
        error_message: str,
        solution: str,
        error_type: Optional[str] = None,
        language: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store an error and its solution.

        Args:
            error_message: The error message encountered
            solution: The solution that fixed the error
            error_type: Type of error (e.g., syntax, runtime, logic)
            language: Programming language
            metadata: Additional metadata

        Returns:
            ID of the stored error solution
        """
        import uuid

        error_id = f"error_{uuid.uuid4()}"

        # Combine error and solution for better retrieval
        document = f"Error: {error_message}\n\nSolution: {solution}"

        # Prepare metadata
        meta = {
            "type": "error_solution",
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if error_type:
            meta["error_type"] = error_type
        if language:
            meta["language"] = language
        if metadata:
            meta.update(metadata)

        # Store the error solution
        self.manager.add_memory(
            documents=[document],
            metadatas=[meta],
            ids=[error_id],
        )

        logger.info(f"Stored error solution: {error_id}")
        return error_id

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
        """
        where = {"type": "code_snippet"}
        if language:
            where["language"] = language

        results = self.manager.query_memory(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        return self._format_results(results)

    def find_similar_tasks(
        self,
        query: str,
        task_type: Optional[str] = None,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find similar task contexts.

        Args:
            query: Query string describing the task
            task_type: Optional filter by task type
            n_results: Number of results to return

        Returns:
            List of similar task contexts with metadata
        """
        where = {"type": "task_context"}
        if task_type:
            where["task_type"] = task_type

        results = self.manager.query_memory(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        return self._format_results(results)

    def find_error_solutions(
        self,
        error_query: str,
        language: Optional[str] = None,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find solutions to similar errors.

        Args:
            error_query: Description of the error
            language: Optional filter by programming language
            n_results: Number of results to return

        Returns:
            List of error solutions with metadata
        """
        where = {"type": "error_solution"}
        if language:
            where["language"] = language

        results = self.manager.query_memory(
            query_texts=[error_query],
            n_results=n_results,
            where=where,
        )

        return self._format_results(results)

    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format query results into a more usable structure.

        Args:
            results: Raw query results from ChromaDB

        Returns:
            Formatted list of results
        """
        formatted = []

        if not results.get("ids") or not results["ids"][0]:
            return formatted

        # Results are nested in lists (one per query)
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):
            result = {
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i],
            }

            # Parse JSON fields in metadata
            if "tags" in metadatas[i]:
                try:
                    result["metadata"]["tags"] = json.loads(metadatas[i]["tags"])
                except (json.JSONDecodeError, TypeError):
                    pass

            if "files_involved" in metadatas[i]:
                try:
                    result["metadata"]["files_involved"] = json.loads(
                        metadatas[i]["files_involved"]
                    )
                except (json.JSONDecodeError, TypeError):
                    pass

            if "dependencies" in metadatas[i]:
                try:
                    result["metadata"]["dependencies"] = json.loads(
                        metadatas[i]["dependencies"]
                    )
                except (json.JSONDecodeError, TypeError):
                    pass

            formatted.append(result)

        return formatted
