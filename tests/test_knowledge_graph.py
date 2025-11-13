"""Tests for knowledge graph manager."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from deepagents.knowledge_graph import KnowledgeGraphManager
from deepagents.neo4j_manager import Neo4jManager
from deepagents.config import DeepAgentConfig


@pytest.fixture
def config():
    """Create test configuration."""
    return DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password="test123"
    )


@pytest.fixture
def mock_neo4j_manager(config):
    """Create mock Neo4j manager."""
    manager = Mock(spec=Neo4jManager)
    manager.config = config
    manager._driver = None
    manager.connect = Mock()
    manager.close = Mock()
    manager.create_indexes = Mock()
    manager.execute_query = Mock(return_value=[{"entity_id": 123, "project_id": 123}])
    return manager


@pytest.mark.asyncio
async def test_knowledge_graph_init(config, mock_neo4j_manager):
    """Test knowledge graph manager initialization."""
    kg = KnowledgeGraphManager(neo4j_manager=mock_neo4j_manager, config=config)
    assert kg.config == config
    assert kg.neo4j_manager == mock_neo4j_manager


@pytest.mark.asyncio
@patch("deepagents.knowledge_graph.Graphiti")
async def test_knowledge_graph_initialize(mock_graphiti_class, config, mock_neo4j_manager):
    """Test initializing knowledge graph."""
    mock_graphiti = AsyncMock()
    mock_graphiti_class.return_value = mock_graphiti

    kg = KnowledgeGraphManager(neo4j_manager=mock_neo4j_manager, config=config)
    await kg.initialize()

    mock_neo4j_manager.connect.assert_called_once()
    mock_neo4j_manager.create_indexes.assert_called_once()
    mock_graphiti_class.assert_called_once_with(
        uri=config.neo4j_uri, user=config.neo4j_username, password=config.neo4j_password
    )


@pytest.mark.asyncio
async def test_add_code_entity(config, mock_neo4j_manager):
    """Test adding a code entity."""
    kg = KnowledgeGraphManager(neo4j_manager=mock_neo4j_manager, config=config)

    entity_id = await kg.add_code_entity(
        entity_type="Function", name="test_function", properties={"description": "A test function"}
    )

    assert entity_id == "123"
    mock_neo4j_manager.execute_query.assert_called()


@pytest.mark.asyncio
async def test_add_project(config, mock_neo4j_manager):
    """Test adding a project."""
    kg = KnowledgeGraphManager(neo4j_manager=mock_neo4j_manager, config=config)

    project_id = await kg.add_project(project_name="test_project", description="A test project")

    assert project_id == "123"
    mock_neo4j_manager.execute_query.assert_called()


@pytest.mark.asyncio
async def test_get_project_context(config, mock_neo4j_manager):
    """Test getting project context."""
    mock_neo4j_manager.execute_query.return_value = [
        {"project": {"name": "test_project"}, "files": [], "functions": [], "classes": []}
    ]

    kg = KnowledgeGraphManager(neo4j_manager=mock_neo4j_manager, config=config)
    context = await kg.get_project_context("test_project")

    assert "project" in context
    assert "files" in context
    assert "functions" in context
    assert "classes" in context
