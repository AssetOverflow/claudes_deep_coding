"""
Claudes Deep Coding - Deep agents with knowledge graph integration.

This package provides a framework for building deep coding agents that use
Neo4j and Graphiti to maintain dynamic knowledge graphs of projects and conversations.
"""

__version__ = "0.1.0"

from .config import DeepAgentConfig
from .neo4j_manager import Neo4jManager
from .knowledge_graph import KnowledgeGraphManager
from .deepagent import DeepAgent

__all__ = [
    "DeepAgentConfig",
    "Neo4jManager",
    "KnowledgeGraphManager",
    "DeepAgent",
]
