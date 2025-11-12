"""Configuration management for Deep Agents."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepAgentConfig(BaseSettings):
    """Configuration for Deep Agent with Neo4j and Graphiti integration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "deepcoding123"

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = None

    # Graphiti Configuration
    graphiti_log_level: str = "INFO"

    # Agent Configuration
    max_iterations: int = 10
    conversation_memory_window: int = 20

    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        if not self.neo4j_uri:
            raise ValueError("NEO4J_URI is required")
        if not self.neo4j_username:
            raise ValueError("NEO4J_USERNAME is required")
        if not self.neo4j_password:
            raise ValueError("NEO4J_PASSWORD is required")
        return True
