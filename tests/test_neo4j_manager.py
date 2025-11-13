"""Tests for Neo4j manager."""

import pytest
from unittest.mock import Mock, patch
from deepagents.neo4j_manager import Neo4jManager
from deepagents.config import DeepAgentConfig
from neo4j.exceptions import ServiceUnavailable, AuthError


@pytest.fixture
def config():
    """Create test configuration."""
    return DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password="test123"
    )


@pytest.fixture
def mock_driver():
    """Create mock Neo4j driver."""
    driver = Mock()
    driver.verify_connectivity = Mock()
    driver.close = Mock()
    return driver


def test_neo4j_manager_init(config):
    """Test Neo4j manager initialization."""
    manager = Neo4jManager(config)
    assert manager.config == config
    assert manager._driver is None


@patch("deepagents.neo4j_manager.GraphDatabase.driver")
def test_neo4j_manager_connect(mock_driver_class, config, mock_driver):
    """Test connecting to Neo4j."""
    mock_driver_class.return_value = mock_driver

    manager = Neo4jManager(config)
    manager.connect()

    mock_driver_class.assert_called_once_with(
        config.neo4j_uri, auth=(config.neo4j_username, config.neo4j_password)
    )
    mock_driver.verify_connectivity.assert_called_once()
    assert manager._driver == mock_driver


@patch("deepagents.neo4j_manager.GraphDatabase.driver")
def test_neo4j_manager_connect_auth_error(mock_driver_class, config):
    """Test connection with authentication error."""
    mock_driver_class.side_effect = AuthError("Invalid credentials")

    manager = Neo4jManager(config)

    with pytest.raises(AuthError):
        manager.connect()


@patch("deepagents.neo4j_manager.GraphDatabase.driver")
def test_neo4j_manager_connect_service_unavailable(mock_driver_class, config):
    """Test connection when service is unavailable."""
    mock_driver_class.side_effect = ServiceUnavailable("Service not available")

    manager = Neo4jManager(config)

    with pytest.raises(ServiceUnavailable):
        manager.connect()


def test_neo4j_manager_close(config, mock_driver):
    """Test closing Neo4j connection."""
    manager = Neo4jManager(config)
    manager._driver = mock_driver

    manager.close()

    mock_driver.close.assert_called_once()
    assert manager._driver is None


@patch("deepagents.neo4j_manager.GraphDatabase.driver")
def test_neo4j_manager_context_manager(mock_driver_class, config, mock_driver):
    """Test Neo4j manager as context manager."""
    mock_driver_class.return_value = mock_driver

    with Neo4jManager(config) as manager:
        assert manager._driver == mock_driver
        mock_driver.verify_connectivity.assert_called_once()

    mock_driver.close.assert_called_once()
