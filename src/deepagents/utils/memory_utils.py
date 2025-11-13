"""Memory utility functions."""

from typing import Any, Dict, List


def format_code_context(results: List[Dict[str, Any]]) -> str:
    """
    Format code search results into a readable context string.

    Args:
        results: List of search results from CodingMemory

    Returns:
        Formatted string with code context
    """
    if not results:
        return "No relevant code found in memory."

    context_parts = []
    context_parts.append("=== Relevant Code from Memory ===\n")

    for i, result in enumerate(results, 1):
        metadata = result.get("metadata", {})
        document = result.get("document", "")
        distance = result.get("distance", 0)

        context_parts.append(f"\n--- Result {i} (similarity: {1 - distance:.2f}) ---")
        context_parts.append(f"Language: {metadata.get('language', 'unknown')}")

        if "description" in metadata:
            context_parts.append(f"Description: {metadata['description']}")

        if "file_path" in metadata:
            context_parts.append(f"File: {metadata['file_path']}")

        if "tags" in metadata:
            tags = metadata["tags"]
            if isinstance(tags, list):
                context_parts.append(f"Tags: {', '.join(tags)}")

        context_parts.append(f"\nCode:\n{document}\n")

    return "\n".join(context_parts)


def format_task_summary(results: List[Dict[str, Any]]) -> str:
    """
    Format task search results into a readable summary string.

    Args:
        results: List of search results from CodingMemory

    Returns:
        Formatted string with task summary
    """
    if not results:
        return "No relevant tasks found in memory."

    summary_parts = []
    summary_parts.append("=== Relevant Tasks from Memory ===\n")

    for i, result in enumerate(results, 1):
        metadata = result.get("metadata", {})
        document = result.get("document", "")
        distance = result.get("distance", 0)

        summary_parts.append(f"\n--- Task {i} (similarity: {1 - distance:.2f}) ---")
        summary_parts.append(f"Type: {metadata.get('task_type', 'unknown')}")

        if "timestamp" in metadata:
            summary_parts.append(f"Date: {metadata['timestamp']}")

        summary_parts.append(f"\nDescription:\n{document}\n")

        if "files_involved" in metadata:
            files = metadata["files_involved"]
            if isinstance(files, list):
                summary_parts.append(f"Files: {', '.join(files)}")

        if "outcomes" in metadata:
            summary_parts.append(f"Outcomes: {metadata['outcomes']}")

    return "\n".join(summary_parts)
