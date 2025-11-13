"""Knowledge graph management using Graphiti and Neo4j."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

from .neo4j_manager import Neo4jManager
from .config import DeepAgentConfig

logger = logging.getLogger(__name__)


class KnowledgeGraphManager:
    """Manages the dynamic knowledge graph for deep coding agents."""

    def __init__(
        self, neo4j_manager: Optional[Neo4jManager] = None, config: Optional[DeepAgentConfig] = None
    ):
        """Initialize knowledge graph manager.

        Args:
            neo4j_manager: Neo4j manager instance. If None, creates a new one.
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or DeepAgentConfig()
        self.neo4j_manager = neo4j_manager or Neo4jManager(self.config)
        self._graphiti: Optional[Graphiti] = None

    async def initialize(self) -> None:
        """Initialize Graphiti with Neo4j connection."""
        try:
            # Connect to Neo4j if not already connected
            if not self.neo4j_manager._driver:
                self.neo4j_manager.connect()

            # Initialize Graphiti
            self._graphiti = Graphiti(
                uri=self.config.neo4j_uri,
                user=self.config.neo4j_username,
                password=self.config.neo4j_password,
            )

            # Create necessary indexes
            self.neo4j_manager.create_indexes()

            logger.info("Knowledge graph manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph manager: {e}")
            raise

    async def add_conversation_episode(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        episode_type: EpisodeType = EpisodeType.message,
    ) -> str:
        """Add a conversation episode to the knowledge graph.

        Args:
            content: The conversation content (user message or assistant response).
            metadata: Additional metadata about the episode.
            episode_type: Type of episode (message, code, etc.).

        Returns:
            Episode ID.
        """
        if not self._graphiti:
            await self.initialize()

        episode_metadata = metadata or {}
        episode_metadata.update(
            {"timestamp": datetime.utcnow().isoformat(), "source": "claude_code_agent"}
        )

        try:
            # Add episode to Graphiti
            await self._graphiti.add_episode(
                name=f"Episode_{datetime.utcnow().timestamp()}",
                episode_body=content,
                episode_type=episode_type,
                reference_time=datetime.utcnow(),
                source_description="Deep coding conversation",
            )

            logger.info(f"Added conversation episode with {len(content)} chars")
            return f"episode_{datetime.utcnow().timestamp()}"
        except Exception as e:
            logger.error(f"Failed to add conversation episode: {e}")
            raise

    async def add_code_entity(
        self,
        entity_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Add a code entity to the knowledge graph.

        Args:
            entity_type: Type of entity (e.g., 'Function', 'Class', 'File', 'Module').
            name: Name of the entity.
            properties: Additional properties of the entity.
            relationships: Related entities and relationship types.

        Returns:
            Entity ID.
        """
        props = properties or {}
        props.update(
            {"type": entity_type, "name": name, "created_at": datetime.utcnow().isoformat()}
        )

        # Create the entity node
        query = f"""
        MERGE (e:Entity:CodeEntity:{entity_type} {{name: $name}})
        SET e += $properties
        RETURN id(e) as entity_id
        """

        result = self.neo4j_manager.execute_query(query, {"name": name, "properties": props})

        entity_id = result[0]["entity_id"] if result else None

        # Create relationships if provided
        if relationships and entity_id:
            for rel in relationships:
                self._create_relationship(
                    entity_id,
                    rel.get("target_name"),
                    rel.get("relationship_type", "RELATES_TO"),
                    rel.get("properties", {}),
                )

        logger.info(f"Added code entity: {entity_type} - {name}")
        return str(entity_id)

    def _create_relationship(
        self, from_id: int, to_name: str, rel_type: str, properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a relationship between entities.

        Args:
            from_id: Source entity ID.
            to_name: Target entity name.
            rel_type: Relationship type.
            properties: Relationship properties.
        """
        props = properties or {}
        props["created_at"] = datetime.utcnow().isoformat()

        query = f"""
        MATCH (from) WHERE id(from) = $from_id
        MATCH (to:Entity {{name: $to_name}})
        MERGE (from)-[r:{rel_type}]->(to)
        SET r += $properties
        """

        self.neo4j_manager.execute_query(
            query, {"from_id": from_id, "to_name": to_name, "properties": props}
        )

    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the knowledge graph using natural language.

        Args:
            query: Natural language search query.
            limit: Maximum number of results to return.

        Returns:
            List of relevant knowledge items.
        """
        if not self._graphiti:
            await self.initialize()

        try:
            # Use Graphiti's search capabilities
            results = await self._graphiti.search(query=query, num_results=limit)

            logger.info(f"Search returned {len(results)} results for query: {query}")
            return [
                {
                    "content": result.content if hasattr(result, "content") else str(result),
                    "score": result.score if hasattr(result, "score") else 1.0,
                    "metadata": result.metadata if hasattr(result, "metadata") else {},
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Failed to search knowledge graph: {e}")
            return []

    async def get_project_context(self, project_name: str) -> Dict[str, Any]:
        """Get comprehensive context about a project.

        Args:
            project_name: Name of the project.

        Returns:
            Dictionary containing project context.
        """
        query = """
        MATCH (p:Project {name: $project_name})
        OPTIONAL MATCH (p)-[:CONTAINS]->(f:File)
        OPTIONAL MATCH (f)-[:DEFINES]->(fn:Function)
        OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
        RETURN p as project, 
               collect(DISTINCT f) as files,
               collect(DISTINCT fn) as functions,
               collect(DISTINCT c) as classes
        """

        result = self.neo4j_manager.execute_query(query, {"project_name": project_name})

        if result:
            return {
                "project": result[0].get("project", {}),
                "files": result[0].get("files", []),
                "functions": result[0].get("functions", []),
                "classes": result[0].get("classes", []),
            }
        return {}

    async def add_project(
        self,
        project_name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a new project to the knowledge graph.

        Args:
            project_name: Name of the project.
            description: Project description.
            metadata: Additional project metadata.

        Returns:
            Project ID.
        """
        props = metadata or {}
        props.update(
            {
                "name": project_name,
                "description": description or "",
                "created_at": datetime.utcnow().isoformat(),
            }
        )

        query = """
        MERGE (p:Project {name: $name})
        SET p += $properties
        RETURN id(p) as project_id
        """

        result = self.neo4j_manager.execute_query(
            query, {"name": project_name, "properties": props}
        )

        project_id = result[0]["project_id"] if result else None
        logger.info(f"Added project: {project_name}")
        return str(project_id)

    async def close(self) -> None:
        """Close connections and cleanup."""
        if self._graphiti:
            await self._graphiti.close()
        self.neo4j_manager.close()
        logger.info("Knowledge graph manager closed")
