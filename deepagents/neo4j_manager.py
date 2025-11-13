"""Neo4j connection and management."""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

from .config import DeepAgentConfig

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Manages Neo4j database connections and operations."""

    def __init__(self, config: Optional[DeepAgentConfig] = None):
        """Initialize Neo4j manager.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or DeepAgentConfig()
        self.config.validate_config()
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self._driver = GraphDatabase.driver(
                self.config.neo4j_uri, auth=(self.config.neo4j_username, self.config.neo4j_password)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.config.neo4j_uri}")
        except AuthError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    @contextmanager
    def session(self, database: str = "neo4j") -> Session:
        """Context manager for Neo4j sessions.

        Args:
            database: Database name to connect to.

        Yields:
            Neo4j session object.
        """
        if not self._driver:
            self.connect()

        session = self._driver.session(database=database)
        try:
            yield session
        finally:
            session.close()

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None, database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results.

        Args:
            query: Cypher query string.
            parameters: Query parameters.
            database: Database name.

        Returns:
            List of result records as dictionaries.
        """
        with self.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def create_indexes(self) -> None:
        """Create necessary indexes for knowledge graph."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.type)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Conversation) ON (c.id)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Conversation) ON (c.timestamp)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Project) ON (p.id)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Project) ON (p.name)",
            "CREATE INDEX IF NOT EXISTS FOR (f:File) ON (f.path)",
            "CREATE INDEX IF NOT EXISTS FOR (f:Function) ON (f.name)",
        ]

        for index_query in indexes:
            try:
                self.execute_query(index_query)
                logger.info(f"Created index: {index_query}")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")

    def clear_database(self) -> None:
        """Clear all nodes and relationships (use with caution!)."""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)
        logger.warning("Database cleared!")

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.

        Returns:
            Dictionary with node and relationship counts.
        """
        node_count_query = "MATCH (n) RETURN count(n) as count"
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"

        node_count = self.execute_query(node_count_query)[0]["count"]
        rel_count = self.execute_query(rel_count_query)[0]["count"]

        return {"nodes": node_count, "relationships": rel_count}

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
