"""Tests for deep agent."""

import pytest
from unittest.mock import Mock, AsyncMock
from deepagents.deepagent import DeepAgent
from deepagents.config import DeepAgentConfig
from deepagents.neo4j_manager import Neo4jManager
from deepagents.knowledge_graph import KnowledgeGraphManager


@pytest.fixture
def config():
    """Create test configuration."""
    return DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password="test123"
    )


@pytest.fixture
def mock_neo4j_manager():
    """Create mock Neo4j manager."""
    manager = Mock(spec=Neo4jManager)
    manager.connect = Mock()
    manager.close = Mock()
    manager.get_stats = Mock(return_value={"nodes": 10, "relationships": 5})
    return manager


@pytest.fixture
def mock_kg_manager():
    """Create mock knowledge graph manager."""
    kg = Mock(spec=KnowledgeGraphManager)
    kg.initialize = AsyncMock()
    kg.add_conversation_episode = AsyncMock()
    kg.add_project = AsyncMock(return_value="project_123")
    kg.add_code_entity = AsyncMock(return_value="entity_123")
    kg.search_knowledge = AsyncMock(return_value=[])
    kg.get_project_context = AsyncMock(return_value={})
    kg.close = AsyncMock()
    return kg


@pytest.mark.asyncio
async def test_deep_agent_init(config, mock_neo4j_manager, mock_kg_manager):
    """Test deep agent initialization."""
    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    assert agent.config == config
    assert agent.neo4j_manager == mock_neo4j_manager
    assert agent.knowledge_graph == mock_kg_manager
    assert agent.conversation_history == []
    assert agent.current_project is None


@pytest.mark.asyncio
async def test_deep_agent_initialize(config, mock_neo4j_manager, mock_kg_manager):
    """Test initializing deep agent."""
    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    await agent.initialize()

    mock_kg_manager.initialize.assert_called_once()
    assert agent._initialized is True


@pytest.mark.asyncio
async def test_set_project(config, mock_neo4j_manager, mock_kg_manager):
    """Test setting a project."""
    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    project_id = await agent.set_project("test_project", "A test project")

    assert agent.current_project == "test_project"
    assert project_id == "project_123"
    mock_kg_manager.add_project.assert_called_once_with(
        project_name="test_project", description="A test project"
    )


@pytest.mark.asyncio
async def test_process_message(config, mock_neo4j_manager, mock_kg_manager):
    """Test processing a message."""
    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    response = await agent.process_message("Test message", context={"test": "context"})

    assert "message" in response
    assert response["message"] == "Test message"
    assert len(agent.conversation_history) == 1
    mock_kg_manager.add_conversation_episode.assert_called()


@pytest.mark.asyncio
async def test_search_knowledge(config, mock_neo4j_manager, mock_kg_manager):
    """Test searching knowledge graph."""
    mock_kg_manager.search_knowledge.return_value = [
        {"content": "result1", "score": 0.9},
        {"content": "result2", "score": 0.8},
    ]

    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    results = await agent.search_knowledge("test query")

    assert len(results) == 2
    mock_kg_manager.search_knowledge.assert_called_once_with("test query", 10)


@pytest.mark.asyncio
async def test_get_project_summary(config, mock_neo4j_manager, mock_kg_manager):
    """Test getting project summary."""
    agent = DeepAgent(
        config=config, neo4j_manager=mock_neo4j_manager, knowledge_graph=mock_kg_manager
    )

    await agent.set_project("test_project")
    summary = await agent.get_project_summary()

    assert summary["project"] == "test_project"
    assert "stats" in summary
    assert summary["stats"]["nodes"] == 10
    assert summary["stats"]["relationships"] == 5
