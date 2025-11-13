"""
Advanced example: Building a knowledge graph from a real codebase.

This example shows how to:
1. Analyze a codebase
2. Extract code structure
3. Build a comprehensive knowledge graph
4. Query relationships and patterns
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

from deepagents import DeepAgent, DeepAgentConfig

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class CodebaseAnalyzer:
    """Analyzes a codebase and builds a knowledge graph."""

    def __init__(self, agent: DeepAgent):
        self.agent = agent

    async def analyze_directory(
        self, directory: Path, extensions: List[str] = [".py", ".js", ".ts", ".java"]
    ) -> Dict[str, Any]:
        """Analyze all code files in a directory.

        Args:
            directory: Directory to analyze.
            extensions: File extensions to include.

        Returns:
            Analysis results.
        """
        files_analyzed = 0
        entities_created = 0

        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                if self._should_skip(file_path):
                    continue

                logger.info(f"Analyzing: {file_path}")

                # Add file entity
                await self.agent.knowledge_graph.add_code_entity(
                    entity_type="File",
                    name=str(file_path),
                    properties={
                        "path": str(file_path),
                        "extension": ext,
                        "size": file_path.stat().st_size,
                    },
                )

                files_analyzed += 1
                entities_created += 1

                # Read and analyze file content
                try:
                    content = file_path.read_text(encoding="utf-8")

                    # Process with the agent
                    await self.agent.process_message(
                        message=f"Analyzing file: {file_path.name}",
                        context={
                            "file_path": str(file_path),
                            "code": content[:500],  # First 500 chars
                            "language": ext[1:],  # Remove the dot
                        },
                    )

                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")

        return {"files_analyzed": files_analyzed, "entities_created": entities_created}

    def _should_skip(self, path: Path) -> bool:
        """Check if a file should be skipped."""
        skip_dirs = {
            "node_modules",
            "__pycache__",
            ".git",
            "venv",
            "env",
            "build",
            "dist",
            ".pytest_cache",
        }

        return any(skip_dir in path.parts for skip_dir in skip_dirs)


async def main():
    """Main function for advanced example."""

    logger.info("Starting advanced codebase analysis...")

    # Initialize agent
    config = DeepAgentConfig()
    agent = DeepAgent(config=config)

    try:
        await agent.initialize()

        # Set up project
        project_id = await agent.set_project(
            project_name="deepagents_analysis",
            description="Analysis of the deepagents codebase itself",
        )
        logger.info(f"Project created: {project_id}")

        # Analyze the deepagents codebase
        analyzer = CodebaseAnalyzer(agent)

        # Get the deepagents directory
        current_dir = Path(__file__).parent.parent / "deepagents"

        if current_dir.exists():
            logger.info(f"Analyzing directory: {current_dir}")
            results = await analyzer.analyze_directory(current_dir)
            logger.info(f"Analysis complete: {results}")
        else:
            logger.warning(f"Directory not found: {current_dir}")

        # Query the knowledge graph
        logger.info("Querying knowledge graph...")

        # Search for specific patterns
        queries = [
            "configuration management",
            "Neo4j database connection",
            "knowledge graph operations",
        ]

        for query in queries:
            logger.info(f"Searching: {query}")
            results = await agent.search_knowledge(query, limit=3)
            logger.info(f"Found {len(results)} results")

        # Get final summary
        summary = await agent.get_project_summary()
        logger.info("Final project summary:")
        logger.info(f"  - Nodes: {summary['stats']['nodes']}")
        logger.info(f"  - Relationships: {summary['stats']['relationships']}")
        logger.info(f"  - Conversations: {summary['conversation_length']}")

    except Exception as e:
        logger.error(f"Error in advanced example: {e}", exc_info=True)
    finally:
        await agent.close()
        logger.info("Analysis complete")


if __name__ == "__main__":
    asyncio.run(main())
