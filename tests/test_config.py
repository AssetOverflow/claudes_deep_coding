"""Tests for configuration management."""

import pytest
from deepagents.config import DeepAgentConfig


def test_config_defaults():
    """Test default configuration values."""
    config = DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password="test123"
    )

    assert config.neo4j_uri == "bolt://localhost:7687"
    assert config.neo4j_username == "neo4j"
    assert config.neo4j_password == "test123"
    assert config.graphiti_log_level == "INFO"
    assert config.max_iterations == 10


def test_config_validation():
    """Test configuration validation."""
    config = DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password="test123"
    )

    assert config.validate_config() is True


def test_config_validation_missing_uri():
    """Test validation fails with missing URI."""
    config = DeepAgentConfig(neo4j_uri="", neo4j_username="neo4j", neo4j_password="test123")

    with pytest.raises(ValueError, match="NEO4J_URI is required"):
        config.validate_config()


def test_config_validation_missing_username():
    """Test validation fails with missing username."""
    config = DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="", neo4j_password="test123"
    )

    with pytest.raises(ValueError, match="NEO4J_USERNAME is required"):
        config.validate_config()


def test_config_validation_missing_password():
    """Test validation fails with missing password."""
    config = DeepAgentConfig(
        neo4j_uri="bolt://localhost:7687", neo4j_username="neo4j", neo4j_password=""
    )

    with pytest.raises(ValueError, match="NEO4J_PASSWORD is required"):
        config.validate_config()
