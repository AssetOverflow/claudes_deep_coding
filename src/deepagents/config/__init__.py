"""Configuration module for deepagents."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class ChromaDBConfig(BaseModel):
    """Configuration for ChromaDB vector database."""

    persist_directory: Path = Field(
        default_factory=lambda: Path(
            os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        ),
        description="Directory where ChromaDB will persist data",
    )
    collection_name: str = Field(
        default_factory=lambda: os.getenv(
            "CHROMA_COLLECTION_NAME", "deepagents_memory"
        ),
        description="Name of the ChromaDB collection",
    )
    host: Optional[str] = Field(
        default_factory=lambda: os.getenv("CHROMA_HOST"),
        description="ChromaDB server host (for client/server mode)",
    )
    port: Optional[int] = Field(
        default_factory=lambda: int(os.getenv("CHROMA_PORT", "8000"))
        if os.getenv("CHROMA_PORT")
        else None,
        description="ChromaDB server port (for client/server mode)",
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic/Claude API."""

    api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key",
    )
    model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model to use",
    )


class DeepAgentsConfig(BaseModel):
    """Main configuration for deepagents."""

    chromadb: ChromaDBConfig = Field(
        default_factory=ChromaDBConfig,
        description="ChromaDB configuration",
    )
    anthropic: AnthropicConfig = Field(
        default_factory=AnthropicConfig,
        description="Anthropic configuration",
    )


# Global config instance
config = DeepAgentsConfig()
